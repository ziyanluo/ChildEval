#encoding=utf-8
import os
import json
import argparse

from tqdm import tqdm
import sys




def load_evaluation_data(eval_file):
    if not os.path.isfile(eval_file):
        raise FileNotFoundError(f"File not found: {eval_file}")
    results =[]
    with open(eval_file, "r", encoding='utf-8') as f:
        for line in f:
           results.append(json.loads(line.strip()))
    return results


def analyze_errors(data):
    stats = {
        "acknowledgement": 0,
        "hallucination": 0,
        "violation": 0,
        "error_unhelpful": 0,
        "error_inconsistent": 0,
        "hallucination_of_preference_violation": 0,
        "preference_unaware_violation": 0,
        "preference_adherence_accuracy": 0,
        "adaption": 0,  # "check_emotionadaption.txt",
        "interaction": 0,  # "check_interaction.txt",
        "development": 0,  # "check_development.txt",
        "engagement": 0,  # "check_engagement.txt"
    }

    for idx, entry in tqdm(enumerate(data)):
        #print(entry['index'])
        if "evaluation_error_analysis" not in entry:
            print("Error: this entry has not been evaluated yet!")
        error_types = entry["evaluation_error_analysis"]
        is_acknowledgement = "yes" in error_types.get("acknow", {}).get("answer", "").lower()
        is_hallucination = is_acknowledgement and "yes" in error_types.get("hallucinate", {}).get("answer", "").lower()
        is_violation = "yes" in error_types.get("violate", {}).get("answer", "").lower()
        #if is_violation:
        #   print(idx)
        is_unhelpful = "no" in error_types.get("helpful", {}).get("answer", "").lower()

        is_inconsistent = is_acknowledgement and not is_hallucination and is_violation and not is_unhelpful
        is_hallucination_of_preference_violation = (
            is_acknowledgement and is_hallucination and is_violation and not is_unhelpful
        )
        is_preference_unaware_violation = not is_acknowledgement and is_violation and not is_unhelpful

        preference_following_accuracy = not any(
            [is_inconsistent, is_hallucination_of_preference_violation, is_preference_unaware_violation, is_unhelpful]
        )
        if not preference_following_accuracy:
           print(idx)
        # Update stats
        #children-oriented  evaluation
        stats["adaption"] += is_adaption
        stats["interaction"] += is_interaction
        stats["development"] += is_development
        stats["engagement"] += is_engagement

        ## preference following
        stats["acknowledgement"] += is_acknowledgement
        stats["hallucination"] += is_hallucination
        stats["violation"] += is_violation
        stats["error_unhelpful"] += is_unhelpful
        print(f"idx:{idx},is_unware:{is_preference_unaware_violation} is_acknowledgement: {is_acknowledgement} is_violation:{is_violation}  and is_unhelpful:{is_unhelpful}")
        stats["error_inconsistent"] += is_inconsistent
        stats["hallucination_of_preference_violation"] += is_hallucination_of_preference_violation
        stats["preference_unaware_violation"] += is_preference_unaware_violation
        stats["preference_adherence_accuracy"] += preference_following_accuracy

    return stats, len(data)


def print_evaluation_results(stats, total_data, args):
    print("\n--- Evaluation Setup ---")
    print(f"Model file: {args.ft}")
    print(f"Inter-Turn Tested: {args.turn}")
    print(f"Task: {args.task}")
    print(f"\n--- Results ---")
    print(f"Total Entries Evaluated: {total_data}")
    print(f"Error Type Distribution:")
    print(f"  Unhelpful Responses: {stats['error_unhelpful']}")
    print(f"  Inconsistent Responses: {stats['error_inconsistent']}")
    print(f"  Hallucination of Preference Violations: {stats['hallucination_of_preference_violation']}")
    print(f"  Preference Unaware Violations: {stats['preference_unaware_violation']}")
    accuracy = (stats["preference_adherence_accuracy"] / total_data) * 100
    print(f"\nPreference Following Accuracy: {accuracy:.2f}%")
    #print children-oriented evaluation
    print(f"\n adaption Responses: {stats['adaption']} Accuracy: {(stats['adaption'] / total_data) * 100:.2f}%")
    print(f"\n interaction Responses: {stats['interaction']} Accuracy: {(stats['interaction'] / total_data) * 100:.2f}%")
    print(f"\n development Responses: {stats['development']} Accuracy: {(stats['development'] / total_data) * 100:.2f}%")
    print(f"\n engagement Responses: {stats['engagement']} Accuracy: {(stats['engagement'] / total_data) * 100:.2f}%")


def main():
    parser = argparse.ArgumentParser(description="Evaluation Setup")
    parser.add_argument("--turn", type=int, default=3)
    parser.add_argument("--task", type=str, default="zero-shot", choices=["zero-shot", "remind"])
    parser.add_argument("--ft", type=str, default="qwen3b")
    parser.add_argument("--input_file", type=str)
    args = parser.parse_args()
    eval_file = args.input_file
    data = load_evaluation_data(eval_file)
    stats, total_data = analyze_errors(data)
    print_evaluation_results(stats, total_data, args)


if __name__ == "__main__":
    main()
