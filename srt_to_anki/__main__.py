from .cli import make_argparser
from .cli import main


if __name__ == "__main__":
    argparser = make_argparser()
    args = argparser.parse_args()
    main(args.srt, output_name=args.name, output_dir=args.output_dir)
