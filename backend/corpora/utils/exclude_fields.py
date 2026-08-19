from textcavator_readers import extract

def has_extractor(field):
    if type(field.extractor) != extract.Constant:
        return True
    return field.extractor.apply() != None

def exclude_fields_without_extractor(fields):
    return list(filter(has_extractor, fields))
