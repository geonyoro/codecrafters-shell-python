def get_common_base(text, progs: list[str]) -> str:
    """Provided a text and a list of progs, returns the common phrase."""
    filtered_progs = [i for i in progs if i.startswith(text)]
    if len(filtered_progs) > 1:
        common_parts = ""
        max_letter_group_size = None
        for letter_group in zip(*filtered_progs):
            first_letter = letter_group[0]
            if max_letter_group_size is None:
                max_letter_group_size = len(letter_group)
            all_letters_similar = all([letter == first_letter  for letter in letter_group[1:]])
            if all_letters_similar  and len(letter_group) == max_letter_group_size:
                common_parts += first_letter
        return common_parts
    elif len(filtered_progs) == 1:
        return filtered_progs[0]
    return ""
