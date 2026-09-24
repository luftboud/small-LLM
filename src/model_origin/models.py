"""Model construction and persistence.

Building models here (rather than inline in cli.py or scripts/run_experiment.py) keeps
one canonical definition of each model, so the CLI's ``train`` command, the notebooks,
and scripts/run_experiment.py can't quietly drift into three different versions of
"the logistic regression model".
"""
