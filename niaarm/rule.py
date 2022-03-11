from dataclasses import dataclass, field, InitVar
import math
from typing import ClassVar
import pandas as pd
from niaarm.feature import Feature


@dataclass(repr=False)
class Rule:
    r"""Class representing an association rule.

    Args:
        antecedent (list[Feature]): A list of antecedents of the association rule.
        consequent (list[Feature]): A list of consequents of the association rule.
        fitness (Optional[float]): Value of the fitness function.

    Attributes:
        cls.metrics (tuple[str]): List of all available metrics.
        support (float): Support of the rule i.e. proportion of transactions containing
         both the antecedent and the consequent.
        confidence (float): Confidence of the rule, defined as the proportion of transactions that contain
         the consequent in the set of transactions that contain the antecedent.
        lift (float): Lift of the rule. Lift measures how many times more often the antecedent and the consequent Y
         occur together than expected if they were statistically independent.
        coverage (float): Coverage of the rule, also known as antecedent support. It measures the probability that
         the rule applies to a randomly selected transaction.
        rhs_support (float): Support of the consequent.
        conviction (float): Conviction of the rule.
        inclusion (float): Inclusion of the rule is defined as the ratio between the number of attributes of the rule
         and all attributes in the dataset.
        amplitude (float): Amplitude of the rule.
        interestingness (float): Interestingness of the rule.
        comprehensibility (float): Comprehensibility of the rule.
        netconf (float): The netconf metric evaluates the interestingness of
         association rules depending on the support of the rule and the
         support of the antecedent and consequent of the rule.
        yulesq (float): Yule's Q metric.

    """

    metrics: ClassVar[tuple[str]] = (
        'support', 'confidence', 'lift', 'coverage', 'rhs_support', 'conviction', 'amplitude', 'inclusion',
        'interestingness', 'comprehensibility', 'netconf', 'yulesq'
    )
    antecedent: list[Feature]
    consequent: list[Feature]
    fitness: float = field(default=0.0, compare=False)
    transactions: InitVar[pd.DataFrame] = None

    def __post_init__(self, transactions):
        self.num_transactions = len(transactions)
        self.__inclusion = (len(self.antecedent) + len(self.consequent)) / len(transactions.columns)
        min_max = transactions.agg(['min', 'max'])
        acc = 0

        contains_antecedent = pd.Series([True] * self.num_transactions)
        for attribute in self.antecedent:
            if attribute.dtype != 'cat':
                feature_min, feature_max = min_max[attribute.name].tolist()
                acc += (attribute.max_val - attribute.min_val) / (feature_max - feature_min)
                contains_antecedent &= transactions[attribute.name] <= attribute.max_val
                contains_antecedent &= transactions[attribute.name] >= attribute.min_val
            else:
                contains_antecedent &= transactions[attribute.name] == attribute.categories[0]

        self.antecedent_count = len(transactions[contains_antecedent])

        contains_consequent = pd.Series([True] * self.num_transactions)
        for attribute in self.consequent:
            if attribute.dtype != 'cat':
                feature_min, feature_max = min_max[attribute.name].tolist()
                acc += (attribute.max_val - attribute.min_val) / (feature_max - feature_min)
                contains_consequent &= transactions[attribute.name] <= attribute.max_val
                contains_consequent &= transactions[attribute.name] >= attribute.min_val
            else:
                contains_consequent &= transactions[attribute.name] == attribute.categories[0]

        self.consequent_count = len(transactions[contains_consequent])
        self.__amplitude = 1 - (1 / (len(self.antecedent) + len(self.consequent))) * acc

        self.full_count = len(transactions[contains_antecedent & contains_consequent])

    @property
    def support(self):
        return self.full_count / self.num_transactions

    @property
    def rhs_support(self):
        return self.consequent_count / self.num_transactions

    @property
    def confidence(self):
        return self.full_count / self.antecedent_count if self.antecedent_count else 0.0

    @property
    def lift(self):
        return self.support / (self.coverage * self.rhs_support)

    @property
    def coverage(self):
        return self.antecedent_count / self.num_transactions

    @property
    def conviction(self):
        return (1 - self.rhs_support) / (1 - self.confidence + 2.220446049250313e-16)

    @property
    def interestingness(self):
        return (self.support / self.rhs_support) * (self.support / self.coverage) * (
                1 - (self.support / self.num_transactions))

    @property
    def yulesq(self):
        num = self.full_count * (self.num_transactions - self.full_count)
        den = (self.full_count - self.consequent_count) * (self.full_count - self.antecedent_count)
        odds_ratio = num / (den + 2.220446049250313e-16)
        return (odds_ratio - 1) / (odds_ratio + 1)

    @property
    def netconf(self):
        return (self.support - self.coverage * self.rhs_support) / (
                    self.coverage * (1 - self.coverage + 2.220446049250313e-16))

    @property
    def inclusion(self):
        return self.__inclusion

    @property
    def amplitude(self):
        return self.__amplitude

    @property
    def comprehensibility(self):
        return math.log(1 + len(self.consequent)) / math.log(1 + len(self.antecedent) + len(self.consequent))

    def __repr__(self):
        return f'{self.antecedent} => {self.consequent}'
