def binary(char):
    """
    Converts a character into a list of its binary representation, starting from the least significant bit.

    Args:
        char (str): The character to be converted to binary.

    Returns:
        list: A list of 8 bits representing the binary representation of the character.
    """

    # Convert character to integer
    char = ord(char)

    b_char = [0 for i in range(8)]

    # Extract each bit from the integer associated with the character
    for b in range(8):
        bit = ((1 << b) & char) >> b
        b_char[b] = bit

    # Return the list with the eight bits of the character
    return b_char


def hamming_encoder_22_16(block):
    """
    Encodes a 16-bit block of data using Hamming (22, 16) error correction code.

    Args:
        block (list): A list of 16 bits representing the data block to be encoded.

    Returns:
        list: A list of 22 bits representing the encoded block with added parity bits.
    """
    # Insert parity bits at positions corresponding to powers of 2 in the block
    # and at position 0 for double error detection
    block.insert(0, 0)
    block.insert(1, 0)
    block.insert(2, 0)
    block.insert(4, 0)
    block.insert(8, 0)
    block.insert(16, 0)

    # Iterate through the entire block, summing the value of each bit of the block
    # to all the parity bits that evaluate that bit. Thus, the position associated with
    # each parity bit in the block will have the sum of the bits it evaluates.
    for i in range(22):        
        if i % 2 > 0:
            block[1] += block[i]

        if i % 4 > 1:
            block[2] += block[i]

        if i % 8 > 3:
            block[4] += block[i]

        if i % 16 > 7:
            block[8] += block[i]

        if i % 32 > 15:
            block[16] += block[i]

    # Check if the sum of the bits evaluated by each parity bit is even or odd,
    # and modify the parity bit value to make it even.
    for i in range(5):
        if block[2**i] % 2 == 1:
            block[2**i] = 1
        else:
            block[2**i] = 0

    # Set the value of bit 0, which checks the parity of the entire block, to make it even.
    if sum(block) % 2 == 1:
        block[0] = 1
    else:
        block[0] = 0

    # Return the block in the format of a list with 22 bits
    return block


def hamming_decoder_22_16(block):
    """
    Decodes a 22-bit block of data encoded with Hamming (22, 16) error correction code.

    Args:
        block (list): A list of 22 bits representing the encoded block with parity bits.

    Returns:
        tuple: A tuple containing the decoded block (list) and an error status (int):
               - If error status is 0, no errors were detected or corrected.
               - If error status is 1, a single error was detected and corrected.
               - If error status is 2, multiple errors were detected and the correction could not be applied.
    """
    # Convert the block to a list from the standard library
    block = list(block)

    # Check the parity of the entire block to determine if there was an even or odd number of errors
    block_parity = sum(block) % 2

    # List of error occurrences in the bits in the regions evaluated by the bits 2**0 to 2**4, respectively
    error = [0, 0, 0, 0, 0]

    # Iterate through the block, summing the value of each bit in the positions of the error vector
    # that evaluate its parity
    for i in range(22):
        if i % 2 > 0:
            error[0] += block[i]

        if i % 4 > 1:
            error[1] += block[i]

        if i % 8 > 3:
            error[2] += block[i]

        if i % 16 > 7:
            error[3] += block[i]

        if i % 32 > 15:
            error[3] += block[i]

    # Check if the parity of each region is even (no error) or odd (error occurred)
    # and set the bits of the 'error' vector to 1 for regions whose corresponding parity
    # indicated the presence of an error, and set them to zero otherwise
    for i in range(len(error)):
        error[i] = error[i] % 2

    # Calculate the position of the error in the block. If it is zero, it indicates that there was no error
    # in the block or there was only an error in the parity bit. If two or more errors occurred, the calculated
    # position will be arbitrary, between 1 and 31
    error_position = sum((error[i] * 2**i for i in range(5)))
    error_position = int(error_position)

    # If an error is identified in a position, but the overall parity is even, multiple errors occurred
    # and in an even number. Also, if the error position is greater than the end of the block, there were multiple errors.
    # In this case, the Hamming code cannot correct the error.
    if (error_position != 0 and block_parity == 0) or error_position >= 22:
        multiple_errors = True
    else:
        multiple_errors = False

    # If only one error is identified, apply the correction
    if not multiple_errors:
        block[error_position] = (block[error_position] + 1) % 2

    # Remove the parity bits, leaving only the data bits
    for i in range(4, -1, -1):
        del block[2**i]
    del block[0]

    # If multiple errors were identified:
    if multiple_errors:
        return block, 2

    # If only one error was identified:
    elif error_position != 0:
        return block, 1

    # If no errors were identified:
    else:
        return block, 0