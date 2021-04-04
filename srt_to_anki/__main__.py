from srt_to_anki import cli


def main():
    argparser = cli.make_argparser()
    args = argparser.parse_args()
    cli.main(args.srt, output_name=args.name, output_dir=args.output_dir)
