import random
import time
import numpy as np
import sk_dsp_comm.fec_conv as fec
from colorama import init, Fore

import hamming_utils

class Hamming:
    def __init__(self):
        init()
        self.original_msg = ""
        self.recovered_msg = ""
        self.sigma = 0

    def get_user_input(self):
        msg_1 = "Enter the message to be sent:"
        msg_2 = "Enter the value of variance σ^2:"
        self.original_msg = str(input(f"{Fore.GREEN}{msg_1}{Fore.RESET}\n"))
        self.sigma = np.sqrt(float(input(f"{Fore.GREEN}{msg_2}{Fore.RESET}\n")))

    def hamming_logic(self):
        # Convert the message to binary form 'h', which is a list where the first eight elements
        # correspond to the bits of the first character of the message, starting from the least significant bit.
        # Then come the bits of the second character and so on.
        h = []
        for character in self.original_msg:
            h += hamming_utils.binary(character)


        # Encode the message into blocks with parity check using the extended Hamming code.
        # Each block consists of 16 data bits, corresponding to two consecutive characters from the uncoded message,
        # and 6 parity bits, totaling 22 bits.
        x_hamming = []
        for i in range(0, len(h) - 16, 16):
            x_hamming += hamming_utils.hamming_encoder_22_16(h[i: i + 16])


        # If the message has an odd number of characters, the last encoded block will consist of
        # 8 data bits from the last character and 8 '0' bits from a NULL character, which will be removed
        # after decoding.
        if len(h) % 16 == 0:
            x_hamming += hamming_utils.hamming_encoder_22_16(h[-16:])
        elif len(h) % 16 == 8:
            x_hamming += hamming_utils.hamming_encoder_22_16(h[-8:] + 8 * [0])


        # Duplicate the encoded message by the Hamming code to better utilize the channel usage limit.
        x_hamming = 2 * x_hamming


        # Create an object to perform the convolution of the already encoded and duplicated message, which will be
        # actually transmitted through the noisy channel.
        # The convolution algorithm uses a rate of 1/3 for the convolved signal and generator polynomials
        # of order 8.
        # The decision depth defines how many state transitions will be considered when recovering
        # the uncoded signal.
        decision_depth = 75
        cc1 = fec.FECConv(('11110111', '11011001', '10010101'), decision_depth)
        state = '0000000'


        # Convolve the already encoded and duplicated message, but first add 'decision_depth - 1'
        # zero bits because the last recovered convolved bit needs 'decision_depth - 1' bits ahead of it
        # since the decoder uses 'decision_depth' state transitions to recover the bit.
        x_hamming_conv, state = cc1.conv_encoder(np.array(x_hamming + (decision_depth - 1) * [0]), state)


        # Convert the fully encoded signal to antipodal form, i.e., zeros become -1 to
        # maximize the distance between code words.
        for i in range(len(x_hamming_conv)):
            if x_hamming_conv[i] == 0:
                x_hamming_conv[i] = -1


        # Add noise with zero mean and standard deviation 'self.sigma' to each component of the
        # transmitted encoded message, generating the observation 'y' of the message seen by the receiver.
        y = []
        for i in range(len(x_hamming_conv)):
            noise = random.gauss(0, self.sigma)
            y.append(x_hamming_conv[i] + noise)
        y = np.array(y)


        # Convert the received message from antipodal form (-1 or 1 + noise) to binary form (0 or 1 + noise/2)
        # Then multiply by (2 ** quant_level - 1), as the decoder will quantize each observation component
        # into a certain number of discrete levels, based on the 'quant_level' parameter.
        quant_level = 5
        yn = ((y + 1) / 2) * (2 ** quant_level - 1)
        # Decode the noisy message, obtaining the recovered Hamming encoded blocks after transmission.
        # The decoding uses the Viterbi algorithm with soft decision, meaning that the information of how close or far
        # from the decision threshold an observation was is used in the estimation of the transmitted message.
        x_hamming_rec = cc1.viterbi_decoder(yn, 'soft', quant_level=quant_level)


        # Decode the Hamming blocks to recover the actual transmitted message, taking into account the two copies
        # of each block that were transmitted.
        h_rec = []
        for i in range(0, len(x_hamming_rec) // 2, 22):
            middle = len(x_hamming) // 2

            # Recover the two versions of each block
            block_v1, error_1 = hamming_utils.hamming_decoder_22_16(x_hamming_rec[i: i + 22])
            block_v2, error_2 = hamming_utils.hamming_decoder_22_16(x_hamming_rec[middle + i: middle + i + 22])

            # Choose the version that identified fewer errors.
            # Each version may have identified no errors, one error that is corrected by the Hamming algorithm,
            # but an odd number of errors (3, 5, ...) can be confused with a single error and thus be
            # erroneously corrected. Or there may be 2 or more identified errors, and in this case, the message
            # of the block cannot be recovered.
            if error_1 <= error_2:
                h_rec += block_v1
            else:
                h_rec += block_v2

        # Check if the last character of the recovered message is NULL, which means it was only used to
        # complete the last Hamming block and is not part of the original message.
        if h_rec[-8:] == 8 * [0]:
            h_rec = h_rec[:-8]


        # Convert the bits recovered from 'h_rec' into characters, forming a string of the recovered message after transmission.
        self.recovered_msg = ""
        for i in range(0, len(h_rec), 8):
            character = sum([h_rec[i + k] * 2 ** k for k in range(8)])
            self.recovered_msg += chr(int(character))


        # Compare the recovered message with the original message to calculate the quantity and error rate.
        self.errors = 0
        for i in range(len(self.original_msg)):
            if self.recovered_msg[i] != self.original_msg[i]:
                self.errors += 1

    def print_results(self):
        print(f"Recovered message: {Fore.GREEN}{self.recovered_msg}{Fore.RESET}")
        print(f"Message size: {Fore.YELLOW}{len(self.original_msg)}{Fore.RESET}")
        print(f"Error rate: {Fore.RED}{100 * self.errors / len(self.recovered_msg): .2f}%{Fore.RESET}")
        print(f"Total errors: {Fore.RED}{self.errors}{Fore.RESET}")

    def run(self):
        self.get_user_input()
        self.hamming_logic()
        self.print_results()

if __name__ == "__main__":
    init()
    # Store the starting time
    start_time = time.time()
    hamming = Hamming()
    hamming.run()
    duration = time.time() - start_time
    print(f"Execution time: {Fore.CYAN}{duration:.2f} seconds{Fore.RESET}")