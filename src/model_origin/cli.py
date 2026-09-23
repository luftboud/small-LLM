"""Single entry point for this project: ``python -m model_origin <command>``.

One CLI with subcommands (rather than three separate scripts) means there's one place
that knows how to load config, set the seed, and set up logging — every command gets
that for free instead of each script reimplementing it slightly differently.
"""
