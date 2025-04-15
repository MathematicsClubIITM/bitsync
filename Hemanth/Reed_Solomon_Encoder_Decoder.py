import numpy as np
import galois

def binary_erasure_channel(codeword, erasure_prob):
        """
        📡 Simulate Binary Erasure Channel (BEC)
        """
        erasures = np.random.rand(len(codeword)) < erasure_prob
        received = codeword.copy()
        received_array = np.array(received, dtype=object)
        received_array[erasures] = "?"  # Erased symbols
        return received_array

class ReedSolomonErrorCorrector:
    def __init__(self, m=4, n=15, k=10, erasure_prob=0.3):
        """
        🎯 Initialize the RS error corrector.
        m: Field degree (GF(2^m)), n: Codeword length, k: Message length
        """
        self.m = m
        self.GF = galois.GF(2 ** m)
        self.n = n
        self.k = k
        self.erasure_prob = erasure_prob

    def rs_encode(self, message):
        """
        🔐 Encode the message using RS(n, k)
        """
        assert len(message) == self.k, "Message length must be k"
        message_poly = galois.Poly(message[::-1], field=self.GF)
        xs = self.GF.Range(1, self.n + 1)
        codeword = [message_poly(x) for x in xs]
        return self.GF(codeword)

    def rs_decode(self, received):
        """
        🧩 Decode using interpolation through known points
        """
        xs = self.GF.Range(1, self.n + 1)
        known_x, known_y = [], []

        for xi, yi in zip(xs, received):
            if yi != "?":
                known_x.append(xi)
                known_y.append(yi)

        if len(known_x) < self.k:
            raise ValueError("❌ Not enough known symbols to recover the message")

        known_x = self.GF(known_x)
        known_y = self.GF(known_y)

        interpolated_poly = galois.lagrange_poly(known_x, known_y)
        msg_coeffs = interpolated_poly.coeffs[::-1]  # Ascending order
        if len(msg_coeffs) < self.k:
            msg_coeffs = np.concatenate([msg_coeffs, [0] * (self.k - len(msg_coeffs))])

        return self.GF(msg_coeffs[:self.k])

    def compute_rate(self):
        """
        📊 Compute code rate
        """
        rate = self.k / self.n

        print(f"\n🎯 RS Code Rate: R = {self.k}/{self.n} = {rate:.2f}")
        return rate

def main():
    m = 4
    k = 10
    n = 15
    erasure_prob = 0.3

    rs_corrector = ReedSolomonErrorCorrector(m=m, n=n, k=k, erasure_prob=erasure_prob)
    print("🔧 Reed-Solomon Error Correction Simulation")
    print(f"📚 Field: GF(2^{m}), Code: RS({n}, {k}), Erasure Prob: {erasure_prob}")

    message = rs_corrector.GF.Random(k)
    print("\n📝 Original Message:", message)

    codeword = rs_corrector.rs_encode(message)
    print("🔐 Encoded Codeword:", codeword)

    received = binary_erasure_channel(codeword, erasure_prob)
    print("📡 Received (with erasures):", received)

    decoded = rs_corrector.rs_decode(received)
    print("🧩 Decoded Message:", decoded)

    success = np.array_equal(message, decoded)
    print(f"✅ Successful Decode: {success}")

    rs_corrector.compute_rate()
    print(f"📡 BEC Capacity (ε = {erasure_prob}): C = 1 - ε = {1 - erasure_prob:.2f}")

# Run the main function
if __name__ == "__main__":
    main()