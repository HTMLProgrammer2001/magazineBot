def parseRange(r: str):
    priceRangeStr = r.replace(' ', '').split('-')
    priceRange = [float(item) for item in priceRangeStr]

    if len(priceRange) != 2:
        raise Exception('Invalid range')

    return priceRange
