age_mapping = {
    "Filhote": 0,
    "Jovem": 1,
    "Adulto": 2,
    "Idoso": 3
}

sex_mapping = {
    "Macho": 0,
    "Femea": 1
}

size_mapping = {
    "Pequeno": 0,
    "Médio": 1,
    "Grande": 2,
}

env_cats_mapping = {
    "Sim": 1,
    "Não": 0,
}

fixed_mapping = {
    "Sim": 1,
    "Não": 0,
}

house_trained_mapping = {
    "Sim": 1,
    "Não": 0,
}

special_needs_mapping = {
    "Sim": 1,
    "Não": 0,
}

shots_current_mapping = {
    "Sim": 1,
    "Não": 0,
}

env_children_mapping = {
    "Sim": 1,
    "Não": 0,
}

env_dogs_mapping = {
    "Sim": 1,
    "Não": 0,
}


def convert_string_to_integer(df):
    """
    Converts string values in a dictionary to integers based on predefined mappings.

    :param df:
    :return: A dictionary with the same keys but with string values converted to integers.
    """

    mapping_dicts = {
        'age': age_mapping,
        'sex': sex_mapping,
        'size': size_mapping,
        'fixed': fixed_mapping,
        'house_trained': house_trained_mapping,
        'special_needs': special_needs_mapping,
        'shots_current': shots_current_mapping,
        'env_children': env_children_mapping,
        'env_dogs': env_dogs_mapping,
        'env_cats': env_cats_mapping,
    }

    for column, mapping_dict in mapping_dicts.items():
        if column in df.columns:
            df[column] = df[column].map(mapping_dict)

    return df


age_reverse_mapping = {v: k for k, v in age_mapping.items()}
sex_reverse_mapping = {v: k for k, v in sex_mapping.items()}
size_reverse_mapping = {v: k for k, v in size_mapping.items()}
fixed_reverse_mapping = {v: k for k, v in fixed_mapping.items()}
house_trained_reverse_mapping = {v: k for k, v in house_trained_mapping.items()}
special_needs_reverse_mapping = {v: k for k, v in special_needs_mapping.items()}
shots_current_reverse_mapping = {v: k for k, v in shots_current_mapping.items()}
env_children_reverse_mapping = {v: k for k, v in env_children_mapping.items()}
env_dogs_reverse_mapping = {v: k for k, v in env_dogs_mapping.items()}
env_cats_reverse_mapping = {v: k for k, v in env_cats_mapping.items()}


def convert_integer_to_string(data_list):
    """
    Converts integer values in a list of dictionaries to strings based on predefined reverse mappings.

    :param data_list: A list of dictionaries containing integer values to be converted.
    :return: A list of dictionaries with the same keys but with integer values converted to strings.
    """
    reverse_mappings = {
        'age': age_reverse_mapping,
        'sex': sex_reverse_mapping,
        'size': size_reverse_mapping,
        'fixed': fixed_reverse_mapping,
        'house_trained': house_trained_reverse_mapping,
        'shots_current': shots_current_reverse_mapping,
        'special_needs': special_needs_reverse_mapping,
        'env_children': env_children_reverse_mapping,
        'env_dogs': env_dogs_reverse_mapping,
        'env_cats': env_cats_reverse_mapping,
    }

    for data_dict in data_list:
        for key, value in data_dict.items():
            if key in reverse_mappings:
                data_dict[key] = reverse_mappings[key].get(value, "Unknown")

    return data_list
