# chaotic-sequences-entropy-analysis
Python scripts for chaotic sequence generation and block entropy analysis, supporting the comparative evaluation of SFDR, statistical properties, and NIST test suites.
## 📂 Repository Structure

```text
├── src/
│   ├── tent_maps.py        # Implementation of Tent chaotic sequence generators
│   ├── Logistic_maps.py        # Implementation of Logistic Chaotic Sequence Generators
│   ├── Individual_sequence_from_bin.py # Separation of 50 sequences of 65535 bits from the original array in the .bin file 
│   ├── Software_sequence.py        # Implementation of SOFTWARE sequence generators
│   ├── rate_entropy.py  # Block entropy calculation
└── README.md
