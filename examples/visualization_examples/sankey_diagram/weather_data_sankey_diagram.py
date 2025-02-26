from examples.visualization_examples.prepare_datasets import get_weather_data
from niaarm import Dataset, get_rules
from niaarm.visualize import sankey_diagram

# Get prepared weather data
arm_df = get_weather_data()

# Prepare Dataset
dataset = Dataset(
    path_or_df=arm_df,
    delimiter=","
)

# Get rules
metrics = ("support", "confidence")
rules, run_time = get_rules(
    dataset=dataset,
    algorithm="DifferentialEvolution",
    metrics=metrics,
    max_evals=500
)

# Add lift after the rules have been generated
# Cannot be in metrics before because get_rules metrics doesn't contain lift, therefore we need to add after
metrics = list(metrics)
metrics.append("lift")
metrics = tuple(metrics)

# Sort rules
rules.sort(by="support")
# Print rule information
print("\nRules:")
print(rules)
print(f'\nTime to generate rules: {f"{run_time:.3f}"} seconds')
print("\nRule information: ", rules[3])
print("Antecedent: ", rules[3].antecedent)
print("Consequent: ", rules[3].consequent)
print("Confidence: ", rules[3].confidence)
print("Support: ", rules[3].support)
print("Lift: ", rules[3].lift)
print("\nMetrics:", metrics)

# Visualize sankey diagram
fig = sankey_diagram(rules=rules, interestingness_measure="support", M=4)
fig.show()
