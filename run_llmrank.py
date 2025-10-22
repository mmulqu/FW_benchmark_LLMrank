import pandas as pd
import networkx as nx
from dotenv import load_dotenv
import os
import llm
import json
from datetime import datetime
from tqdm import tqdm
import time
import random
import argparse

# Load environment variables
load_dotenv()

def get_models():
    """Parse command-line arguments to get the list of models."""
    parser = argparse.ArgumentParser(description="Run LLM rankings.")
    parser.add_argument(
        "-m",
        "--models",
        nargs="+",
        help="List of models to evaluate",
        default=["gpt-4o", "o3-mini", "anthropic/claude-3-5-sonnet-20241022"],
    )
    args = parser.parse_args()
    return args.models

MODELS = get_models()

def ensure_results_dir():
    """Create results directory if it doesn't exist."""
    if not os.path.exists('results'):
        os.makedirs('results')

def read_prompts(file_path):
    """Read prompts from Excel file."""
    return pd.read_excel(file_path)

def get_model_responses(prompts, models):
    """Get responses from each model for each prompt with context retention."""
    responses = {}
    conversations = {model: [] for model in models}  # Store conversation history for each model
    total_steps = len(models) * len(prompts)
    
    with tqdm(total=total_steps, desc="Getting responses") as pbar:
        for model in models:
            responses[model] = []
            m = llm.get_model(model)
            pbar.write(f"\nGetting responses from {model}...")
            
            for prompt in prompts['Questions']:
                max_retries = 3
                retry_count = 0
                while retry_count < max_retries:
                    try:
                        time.sleep(random.uniform(1.0, 2.0))
                        
                        # Build context from conversation history
                        context = "\n\n".join([
                            f"Previous Q: {prev_prompt}\nPrevious A: {prev_response}"
                            for prev_prompt, prev_response in conversations[model]
                        ])
                        
                        # Combine context and current prompt
                        full_prompt = (
                            "Consider the following context from our previous conversation:\n\n"
                            f"{context}\n\n"
                            "Current question: " + prompt
                        ) if context else prompt
                        
                        # Get response
                        response = m.prompt(full_prompt)
                        response_str = str(response)
                        
                        # Store response
                        responses[model].append(response_str)
                        
                        # Update conversation history
                        conversations[model].append((prompt, response_str))
                        break
                        
                    except Exception as e:
                        retry_count += 1
                        if retry_count == max_retries:
                            print(f"\nFailed after {max_retries} retries for model {model} on prompt: {prompt[:100]}...")
                            print(f"Error: {str(e)}")
                            responses[model].append("Error: Failed to get response after retries")
                            conversations[model].append((prompt, "Error: Failed to get response"))
                        else:
                            wait_time = retry_count * 5
                            print(f"\nRetrying in {wait_time} seconds... (Attempt {retry_count + 1}/{max_retries})")
                            time.sleep(wait_time)
                            
                pbar.update(1)
    
    return responses

def evaluate_responses(responses, models):
    """Have models evaluate each other's responses."""
    scores = {model: {} for model in models}
    eval_prompt = "You are a judge evaluating AI responses. Rate the following response on a scale of 1-10, where 10 is excellent. Return only the numeric score, nothing else: "
    
    # Calculate total evaluations needed
    total_evals = sum(len(responses[model]) for model in models) * (len(models) - 1)
    
    with tqdm(total=total_evals, desc="Evaluating responses") as pbar:
        for evaluator in models:
            m = llm.get_model(evaluator)
            pbar.write(f"\nGetting evaluations from {evaluator}...")
            for responder in models:
                if evaluator != responder:
                    scores[evaluator][responder] = []
                    for response in responses[responder]:
                        score_response = m.prompt(eval_prompt + response)
                        try:
                            # Convert Response object to string and extract number
                            score_text = str(score_response)
                            # Extract first number from the response
                            score_str = ''.join([c for c in score_text if c.isdigit() or c == '.'])
                            score = float(score_str[:2]) if score_str else 5  # Take first 2 digits max
                            # Ensure score is between 1 and 10
                            score = max(1, min(10, score))
                            scores[evaluator][responder].append(score)
                        except Exception as e:
                            print(f"\nError parsing score ({str(e)}), using default score of 5")
                            scores[evaluator][responder].append(5)  # default score if parsing fails
                        pbar.update(1)
    
    return scores

def calculate_rankings(scores, models):
    """Calculate PageRank scores for models."""
    G = nx.DiGraph()
    
    for evaluator in models:
        for responder in models:
            if evaluator != responder:
                avg_score = sum(scores[evaluator][responder]) / len(scores[evaluator][responder])
                G.add_edge(evaluator, responder, weight=avg_score)
    
    pagerank = nx.pagerank(G)
    return pagerank

def save_results(prompts, responses, scores, rankings):
    """Save all results to files."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    ensure_results_dir()
    
    print("\nSaving results...")
    # Save responses
    responses_df = pd.DataFrame()
    for model in MODELS:
        responses_df[f"{model}_response"] = responses[model]
    responses_df['prompt'] = prompts['Questions']
    responses_df.to_csv(f'results/responses_{timestamp}.csv', index=False)
    
    # Save scores
    with open(f'results/scores_{timestamp}.json', 'w') as f:
        json.dump(scores, f, indent=4)
    
    # Save rankings
    rankings_df = pd.DataFrame(list(rankings.items()), columns=['model', 'score'])
    rankings_df = rankings_df.sort_values('score', ascending=False)
    rankings_df.to_csv(f'results/rankings_{timestamp}.csv', index=False)
    
    # Save a summary text file
    with open(f'results/summary_{timestamp}.txt', 'w') as f:
        f.write("=== PageRank Rankings ===\n")
        for model, score in sorted(rankings.items(), key=lambda x: x[1], reverse=True):
            f.write(f"{model}: {score:.6f}\n")
        f.write("\n=== Average Scores ===\n")
        for evaluator in scores:
            f.write(f"\nScores given by {evaluator}:\n")
            for responder in scores[evaluator]:
                avg_score = sum(scores[evaluator][responder]) / len(scores[evaluator][responder])
                f.write(f"  To {responder}: {avg_score:.2f}\n")
    
    print(f"Results saved with timestamp: {timestamp}")

def main():
    # Read prompts
    prompts = read_prompts('C:/Users/mmulq/Projects/sloprank/LLMRank-main/LLMRank-main/FW_short.xlsx')
    print(f"Loaded {len(prompts)} prompts")
    
    # Get responses
    responses = get_model_responses(prompts, MODELS)
    
    # Get evaluations
    scores = evaluate_responses(responses, MODELS)
    
    # Calculate rankings
    print("\nCalculating rankings...")
    rankings = calculate_rankings(scores, MODELS)
    
    # Save all results
    save_results(prompts, responses, scores, rankings)
    
    # Print results
    print("\n=== PageRank Rankings ===")
    for model, score in sorted(rankings.items(), key=lambda x: x[1], reverse=True):
        print(f"{model}: {score:.6f}")

if __name__ == "__main__":
    main()