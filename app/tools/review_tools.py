"""Custom review tools used by the Reviewer Agent."""

from typing import Mapping, Sequence


def has_required_sections(output: str, required_sections: Sequence[str]) -> bool:
    normalized_output: str = output.lower()

    return all(
        section.lower() in normalized_output
        for section in required_sections
    )


def find_missing_requested_topics(
    user_input: str,
    final_output: str,
    required_assignment_topics: Mapping[str, Sequence[str]],
) -> list[str]:
    normalized_input = user_input.lower()
    normalized_output = final_output.lower()
    missing_topics: list[str] = []

    for topic, keywords in required_assignment_topics.items():
        user_requested_topic = any(keyword in normalized_input for keyword in keywords)
        output_mentions_topic = any(keyword in normalized_output for keyword in keywords)

        if user_requested_topic and not output_mentions_topic:
            missing_topics.append(topic)

    return missing_topics