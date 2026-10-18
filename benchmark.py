import timeit

def with_list(n):
    config_local_device_id = "local"
    secondary_device_ids = [str(i) for i in range(n)] + [str(i) for i in range(n)] # Add duplicates

    existing_sec_ids = []
    for did in secondary_device_ids:
        if did and did != config_local_device_id and did not in existing_sec_ids:
            existing_sec_ids.append(did)
    return existing_sec_ids

def with_set(n):
    config_local_device_id = "local"
    secondary_device_ids = [str(i) for i in range(n)] + [str(i) for i in range(n)] # Add duplicates

    existing_sec_ids = set()
    for did in secondary_device_ids:
        if did and did != config_local_device_id:
            existing_sec_ids.add(did)
    return list(existing_sec_ids)

print("List (10000):", timeit.timeit("with_list(10000)", globals=globals(), number=100))
print("Set (10000):", timeit.timeit("with_set(10000)", globals=globals(), number=100))
