import pandas as pd

# Analyze FW_prompts.xlsx
print("=" * 60)
df_full = pd.read_excel('FW_prompts.xlsx')
print(f'FW_prompts.xlsx: {len(df_full)} prompts')
print(f'Columns: {list(df_full.columns)}')
print(f'\nFirst 5 questions:')
for i, q in enumerate(df_full['Questions'].head(5), 1):
    print(f'{i}. {str(q)[:120]}...')

print("\n" + "=" * 60)
# Analyze FW_short.xlsx
df_short = pd.read_excel('FW_short.xlsx')
print(f'FW_short.xlsx: {len(df_short)} prompts')
print(f'Columns: {list(df_short.columns)}')
print(f'\nAll questions:')
for i, q in enumerate(df_short['Questions'], 1):
    print(f'{i}. {str(q)[:120]}...')

print("\n" + "=" * 60)
print("COST CALCULATION FOR DIFFERENT SCENARIOS:")
print("=" * 60)

def estimate_tokens(text, multiplier=1.3):
    """Rough estimate: 1 word ≈ 1.3 tokens"""
    return int(len(str(text).split()) * multiplier)

def calculate_costs(num_models, num_prompts, avg_prompt_tokens, avg_response_tokens):
    """Calculate API costs for the evaluation"""
    # Phase 1: Get responses from all models
    response_calls = num_models * num_prompts
    response_input_tokens = response_calls * avg_prompt_tokens
    response_output_tokens = response_calls * avg_response_tokens

    # Phase 2: Cross-evaluation (each model evaluates others)
    # With use_subset_evaluation=True, evaluators_subset_size=3
    # Each model evaluates 3 random other models per prompt
    subset_size = min(3, num_models - 1)
    eval_calls = num_models * num_prompts * subset_size
    # Each eval includes the prompt + the response being evaluated
    eval_input_tokens = eval_calls * (avg_prompt_tokens + avg_response_tokens)
    eval_output_tokens = eval_calls * 50  # Short JSON output like {"Model_1": 7}

    total_input_tokens = response_input_tokens + eval_input_tokens
    total_output_tokens = response_output_tokens + eval_output_tokens
    total_tokens = total_input_tokens + total_output_tokens

    return {
        'response_calls': response_calls,
        'eval_calls': eval_calls,
        'total_calls': response_calls + eval_calls,
        'input_tokens': total_input_tokens,
        'output_tokens': total_output_tokens,
        'total_tokens': total_tokens
    }

# Estimate average prompt and response tokens
sample_prompts = df_full['Questions'].head(10).tolist()
avg_prompt_tokens = sum(estimate_tokens(p) for p in sample_prompts) / len(sample_prompts)
avg_response_tokens = 200  # Rough estimate for response length

print(f"\nEstimated avg tokens per prompt: {int(avg_prompt_tokens)}")
print(f"Estimated avg tokens per response: {avg_response_tokens}")

# Scenario comparisons
scenarios = [
    (3, len(df_short), "3 models, FW_short"),
    (5, len(df_short), "5 models, FW_short"),
    (3, len(df_full), "3 models, FW_prompts (full)"),
    (5, len(df_full), "5 models, FW_prompts (full)"),
    (10, len(df_short), "10 models, FW_short"),
    (10, len(df_full), "10 models, FW_prompts (full)"),
]

for num_models, num_prompts, desc in scenarios:
    stats = calculate_costs(num_models, num_prompts, avg_prompt_tokens, avg_response_tokens)
    print(f"\n{desc}:")
    print(f"  Total API calls: {stats['total_calls']:,}")
    print(f"  Total tokens: {stats['total_tokens']:,}")
    print(f"  Approx cost at $1/1M tokens: ${stats['total_tokens']/1_000_000:.2f}")
