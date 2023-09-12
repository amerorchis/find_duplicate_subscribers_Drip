import multiprocessing

def multiprocess_checks(emails_by_first_letter, check_equivalence_function):
    # Create a multiprocessing pool
    pool = multiprocessing.Pool()

    results = []

    # Create a list of tasks to be executed
    tasks = []

    for first_letter, emails in emails_by_first_letter.items():
        task = pool.apply_async(check_equivalence_function, (emails,))
        tasks.append((first_letter, task))

    # Close the pool and wait for all processes to finish
    pool.close()
    pool.join()

    # Collect results
    for first_letter, task in tasks:
        result = task.get()
        results.extend(result)

    return results
