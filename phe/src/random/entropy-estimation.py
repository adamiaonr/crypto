def gen_random_seq(size):

    random_seq = []
    timestamp = 0
    for i in np.arange(size):
        timestamp += randint(1, 50)
        random_seq.append(timestamp)

    return random_seq



def get_coeffs(diffs, seq_index):

    if seq_index < len(diffs):
        return []

    coeffs = OrderedDict()
    for d in diffs:

        if d not in coeffs:
            coeffs[d] = 0

        coeffs[d] = diffs[d][seq_index - d]

    return coeffs

def pred_random_seq_from(seq_index, size, diffs):

    predicted_seq = []

    # get the coefficients from the seq. index
    coeffs = get_coeffs(diffs, seq_index)
    predicted_seq.append(int(coeffs[0]))

    # start the re-construction of the sequence
    for i in np.arange(size - seq_index - 1):

        # update the coefficients
        for d in coeffs:
            if d == (len(coeffs) - 1):
                break
            coeffs[d] += diffs[d + 1][seq_index - i]

        # update the sequence (i.e. from coeffs[0])
        predicted_seq.append(int(coeffs[0]))

    return predicted_seq


    seq_size = int(args.seq_size)
    diff_order = int(args.diff_order)
    p_from = int(args.predict_from)

    random_seq = gen_random_seq(seq_size)
    diffs = calc_diffs(random_seq, diff_order)

    print(diffs[0][(p_from):])
    print(get_coeffs(diffs, p_from))
    print(pred_random_seq_from(p_from, seq_size, diffs))