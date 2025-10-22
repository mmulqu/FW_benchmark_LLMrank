# Getting Started with SlopRank

SlopRank is a framework for ranking LLMs using peer-based cross-evaluation and PageRank. Models evaluate each other's responses to create unbiased, dynamic rankings.

## Prerequisites

- Python 3.8 or higher
- [Simon Willison's `llm` library](https://github.com/simonw/llm)
- API keys for the LLM providers you want to test

## Installation

### 1. Install SlopRank

```bash
pip install sloprank
```

Or install from source:
```bash
cd LLMRank-main/LLMRank-main
pip install .
```

### 2. Install the `llm` CLI tool

```bash
pip install llm
```

### 3. Set up API keys

Set your API keys using the `llm` tool:

```bash
llm keys set openai
# Enter your OpenAI API key when prompted

llm keys set anthropic
# Enter your Anthropic API key when prompted

llm keys set gemini
# Enter your Google API key when prompted
```

## Prepare Your Prompts

Create an Excel file (`.xlsx`) with your test prompts. The file should have at least a `Questions` column:

| Questions |
|-----------|
| What is the capital of France? |
| Explain quantum computing in simple terms |
| Write a haiku about coding |

You can use the provided example files: `prompts.xlsx`, `FW_short.xlsx`, or `FW_prompts.xlsx`

## Running SlopRank

### Basic Usage

Run with default models and config:

```bash
sloprank --prompts prompts.xlsx --output-dir results
```

### Custom Models

Specify which models to evaluate:

```bash
sloprank --prompts prompts.xlsx --output-dir results \
         --models "gpt-4o,claude-3-5-sonnet-latest,gemini-2.0-flash-thinking-exp-1219"
```

### Using the Alternative Script

You can also use `run_llmrank.py` for a simpler workflow:

```bash
python run_llmrank.py --models "gpt-4o" "o3-mini" "anthropic/claude-3-5-sonnet-20241022"
```

## Understanding the Output

Results are saved in the specified output directory with timestamped files:

- **`rankings_[timestamp].csv`** - Final PageRank scores for each model
- **`responses_[timestamp].csv`** - All model responses to prompts
- **`scores_[timestamp].json`** - Detailed evaluation scores between models
- **`summary_[timestamp].txt`** - Human-readable summary of rankings

### Example Output

```
=== PageRank Rankings ===
model                                   score
gpt-4o                                  0.178305
deepseek-chat                           0.167105
gemini-2.0-flash-thinking-exp-1219     0.164732
```

## Configuration

Edit `sloprank/config.py` to customize:

- **`model_names`** - Default models to evaluate
- **`evaluation_method`** - 1 for numeric ratings (1-10), 2 for upvote/downvote
- **`use_subset_evaluation`** - Reduce API costs by limiting evaluations
- **`evaluators_subset_size`** - Number of models each evaluator reviews
- **`request_delay`** - Delay between API requests (to avoid rate limits)

## Quick Start Example

```bash
# 1. Install
pip install sloprank llm

# 2. Set up API keys
llm keys set openai
llm keys set anthropic

# 3. Run evaluation
sloprank --prompts FW_short.xlsx --output-dir results

# 4. View results
cat results/summary_*.txt
```

## Tips

- Start with a small prompt set (`FW_short.xlsx`) to test your setup
- Use `--models` to test specific models before running full evaluations
- Check the `results/` directory for detailed output files
- Set `request_delay` in config if you hit rate limits
- The evaluation process can take time - number of API calls = (# models × # prompts) + (# models × (# models - 1) × # prompts)

## Troubleshooting

**Models not found**: Make sure the model names match those in the `llm` library. Run `llm models list` to see available models.

**API errors**: Verify your API keys are set correctly with `llm keys path`.

**Rate limits**: Increase `request_delay` in `config.py` or reduce `evaluators_subset_size`.

## Next Steps

- Customize the model list in `config.py` for your use case
- Create domain-specific prompt sets for specialized rankings
- Explore the notebook `llmrank.ipynb` for more detailed analysis
- Check `readme.md` for advanced features and contribution ideas

