import sys, argparse, os, pkgutil, inspect

from .options import Options
from .interpreter import Interpreter
from .finder import ExampleFinder, MatchFinder
from .runner import ExampleRunner, Checker
from .parser import ExampleParser
from .reporter import SimpleReporter
from .common import log, build_exception_msg

def parse_args():
    class CSV(argparse.Action):
        def __call__(self, parser, namespace, values, option_string=None):
            # -l a,b  => [a, b]
            values = values.split(',')
            getattr(namespace, self.dest).extend(values)

    search_default = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'modules')
    parser = argparse.ArgumentParser()
    parser.add_argument("files", nargs='+', metavar='file',
                        help="file that have the examples to run.")
    parser.add_argument("-f", "--fail-fast", "--ff", action='store_true',
                        help="if an example fails, fail and stop all the execution.")
    parser.add_argument("--dry", action='store_true',
                        help="do not run any example, only parse them.")
    parser.add_argument("--skip", nargs='+', metavar='file', default=[],
                        help='skip these files')
    parser.add_argument("--search", action='append', metavar='dir',
                        default=[search_default],
                        help='append a directory for searching modules there.')
    parser.add_argument("-d", "--diff", choices=['unified', 'ndiff', 'context'],
                        help='select diff algorithm.')
    parser.add_argument("--no-enhance-diff", action='store_false',
                        dest='enhance_diff',
                        help='by default, some non-printable characters are replaced ' +\
                             'by printable ones in the diffs to make them easier to spot; ' +\
                             'this flag disables that.')
    parser.add_argument("-l", "--language", metavar='language',
                        dest='languages',
                        action=CSV,
                        required=True,
                        default=[],
                        help='select which languages to parse and run. '+
                             'Comma separated syntax is also accepted.')
    parser.add_argument("--encoding",
                        default=sys.stdout.encoding,
                        help='select the encoding (supported in Python 3 only, ' + \
                             'use the same encoding of stdout by default)')
    parser.add_argument("--no-color", action='store_true',
                        help="do not output any escape sequence for coloring.")

    group = parser.add_mutually_exclusive_group()
    group.add_argument("-v", action='count', dest='verbosity', default=0,
                        help="verbosity level, add more flags to increase the level.")
    group.add_argument("-q", "--quiet", action='store_true',
                        help="quiet mode, do not print anything even if an example fails.")

    return parser.parse_args()

def is_a(target_class, key_attr):
    def _is_X(obj):
        if not inspect.isclass(obj):
            return False

        return issubclass(obj, target_class) and \
               obj is not target_class and \
               hasattr(obj, key_attr)

    return _is_X

def load_modules(dirnames, verbosity, encoding):
    registry = {'interpreters': {},
                'finders': {},
                'parsers': {},
                }
    for importer, name, is_pkg in pkgutil.iter_modules(dirnames):
        path = importer.path

        log("From '%s' loading '%s'..." % (path, name), verbosity-2)

        try:
            module = importer.find_module(name).load_module(name)
        except Exception as e:
            log("From '%s' loading '%s'...failed: %s" % (path, name, str(e)),
                                                        verbosity-2)
            continue

        log("From '%s' loaded '%s'" % (path, name), verbosity-1)
        for klass, key, what in [(Interpreter, 'language', 'interpreters'),
                                 (ExampleParser, 'language', 'parsers'),
                                 (MatchFinder, 'target', 'finders')]:

            predicate = is_a(klass, key)

            container = registry[what]
            klasses_found = inspect.getmembers(module, predicate)
            if klasses_found:
                klasses_found = list(zip(*klasses_found))[1]

                # remove already loaded
                klasses_found = set(klasses_found) - set(container.values())

            objs = [klass(verbosity, encoding) for klass in klasses_found]
            if objs:
                log("\n".join((" - %s" % repr(i)) for i in objs), verbosity-1)
                for obj in objs:
                    container[getattr(obj, key)] = obj

    return registry

def get_allowed_languages(registry, selected):
    available = set([obj.language for obj in registry['interpreters'].values()] + \
                      [obj.language for obj in registry['parsers'].values()])

    selected = set(selected)
    not_found = selected - available

    if not_found:
        raise ValueError("The following languages were specified " + \
                         "but they were not found in any module:\n%s" %
                                (str(not_found)))
    return selected

def get_encoding(encoding, verbosity):
    if sys.version_info[0] <= 2: # version major
        # we don't support a different encoding
        encoding = None

    log("Encoding: %s." % encoding, verbosity-2)
    return encoding

def main():
    args = parse_args()

    encoding = get_encoding(args.encoding, args.verbosity)
    registry = load_modules(args.search, args.verbosity, encoding)

    allowed_languages = get_allowed_languages(registry, args.languages)

    allowed_files = set(args.files) - set(args.skip)
    testfiles = [f for f in args.files if f in allowed_files]

    reporter = SimpleReporter(sys.stdout, not args.no_color,
                              args.quiet, args.verbosity)
    checker  = Checker()
    options  = Options(FAIL_FAST=args.fail_fast, WS=False, PASS=False,
                       SKIP=False, ENHANCE_DIFF=args.enhance_diff,
                       TIMEOUT=2,
                       UDIFF=args.diff=='unified',
                       NDIFF=args.diff=='ndiff',
                       CDIFF=args.diff=='context'
                       )

    finder = ExampleFinder(allowed_languages, args.verbosity, registry)
    runner = ExampleRunner(reporter, checker, args.verbosity)

    exit_status = 0
    for filename in testfiles:
        examples = finder.get_examples_from_file(options, filename, encoding)
        if args.dry:
            continue

        result = runner.run(examples, options, filename)
        failed, aborted_or_crashed = result

        if failed:
            exit_status = max(exit_status, 1)

        if aborted_or_crashed:
            exit_status = max(exit_status, 2)

        if (failed or aborted_or_crashed) and options['FAIL_FAST']:
            break

    return exit_status
