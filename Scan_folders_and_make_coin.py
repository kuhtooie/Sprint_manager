import hashlib
import GeneticChunkGenerator
import csv
import os
from pathlib import Path
from tkinter import filedialog
import tkinter as tk
import time 
from typing import List, Dict, Any, Optional


class MerkleTree:
    """
    Production-grade Merkle Tree engine utilizing double SHA-256 (SHA-256d) hashing.
    Replaces legacy single-string hashing with binary tree layer aggregation.
    """

    @staticmethod
    def sha256d(data: bytes) -> bytes:
        """Executes double SHA-256 hashing (SHA-256d) on byte input."""
        return hashlib.sha256(hashlib.sha256(data).digest()).digest()

    @classmethod
    def compute_root(cls, transactions: List[bytes]) -> str:
        """
        Computes the Merkle Root hash from a list of raw transaction byte payloads.

        :param transactions: List of serialized transaction byte payloads.
        :return: 64-character hex string representing the Merkle Root.
        """
        if not transactions:
            return cls.sha256d(b"").hex()

        # Step 1: Compute Leaf Hashes
        current_layer: List[bytes] = [cls.sha256d(tx) for tx in transactions]

        # Step 2: Layer Aggregation Loop
        while len(current_layer) > 1:
            if len(current_layer) % 2 != 0:
                current_layer.append(current_layer[-1])

            next_layer: List[bytes] = []
            for i in range(0, len(current_layer), 2):
                left_node = current_layer[i]
                right_node = current_layer[i + 1]
                parent_node = cls.sha256d(left_node + right_node)
                next_layer.append(parent_node)

            current_layer = next_layer

        return current_layer[0].hex()


class handle_Crypto:

    def __init__(self):
        # Ledger array of all validated coins/blocks
        self.coins: List[Dict[str, Any]] = []
        # Tip Selection Rule: Reference pointer to the tip of the chain with the highest work
        self.current_tip_hash: Optional[str] = None
        self.accumulated_chain_work: int = 0

    @staticmethod
    def calculate_block_work(target_prefix: str = "0000") -> int:
        """
        Accumulated Proof-of-Work Calculation:
        Computes expected hash trials required for difficulty target (2^bits).
        For a 4-zero hexadecimal prefix ('0000'), work = 16^4 = 65,536 units.
        """
        zero_count = len(target_prefix)
        return 16 ** zero_count

    def select_tip(self, candidate_block: Dict[str, Any]) -> bool:
        """
        Tip Selection Rule:
        Evaluates candidate branch against current cumulative chain work.
        Updates global tip pointer if candidate branch represents the heaviest chain.
        """
        candidate_work = candidate_block.get('accumulated_work', 0)
        
        if candidate_work > self.accumulated_chain_work:
            self.current_tip_hash = candidate_block['sha']
            self.accumulated_chain_work = candidate_work
            print(f"[Tip Selection] New active tip updated: {self.current_tip_hash[:10]}... | Total Work: {self.accumulated_chain_work}")
            return True
        else:
            print(f"[Fork Rejection] Block work ({candidate_work}) <= current tip work ({self.accumulated_chain_work}).")
            return False

    def make_coin(self, text: str):

        hash_root = getattr(coin_cloud, 'get_root_hash', lambda: "0" * 64)()
        text += hash_root
        for i in range(200):
            gen = GeneticChunkGenerator.GeneticChunkGenerator()
            gen.get_shas()
            text += gen.code
            ggg = gen.generate_population(len(text))
            for ii in range(len(ggg)):
                text += ggg[ii]['genome']

        # 2. Compute proper binary Merkle Root from payload transactions
        timestamp = int(time.time())
        
        # Split text payload into discrete transaction chunks for binary tree hashing
        chunk_size = 1024
        tx_chunks = [text[i:i + chunk_size].encode('utf-8') for i in range(0, len(text), chunk_size)]
        merkle_root = MerkleTree.compute_root(tx_chunks)

        # 3. Mine the Block Header
        nonce = 0
        header_hash = ""
        difficulty_prefix = "0000"
        
        while not header_hash.startswith(difficulty_prefix):
            nonce += 1
            # Concatenate header fields WITH the nonce
            header_data = f"{hash_root}:{timestamp}:{merkle_root}:{nonce}"
            header_hash = hashlib.sha512(header_data.encode()).hexdigest() 
     
        # 4. Calculate Accumulated Work & Enforce Tip Selection Rule
        block_work = self.calculate_block_work(difficulty_prefix)
        new_accumulated_work = self.accumulated_chain_work + block_work

        block_data = {
            'text': text,
            'merkle': merkle_root,
            'sha': header_hash,
            'prev_hash': hash_root,
            'nonce': nonce,
            'timestamp': timestamp,
            'block_work': block_work,
            'accumulated_work': new_accumulated_work
        }

        # Apply tip selection rule to ensure candidate block extends the heaviest chain
        if self.select_tip(block_data):
            self.save_coins(block_data)

    def get_root(self) -> str:
        """Prompts user to select a names.csv file, reads all related employee CSV fields,
        and returns all text concatenated into a single variable with no spaces.
        """
        # Ensure Tkinter root exists for file dialog without showing a main window
        root_exists = tk._default_root is not None
        root_win = tk._default_root if root_exists else tk.Tk()
        if not root_exists:
            root_win.withdraw()

        # Step 1: Open file dialog to select names.csv
        file_path = filedialog.askopenfilename(
            title="Select the 'names.csv' file",
            filetypes=[("CSV Files", "*.csv"), ("All Files", "*.*")],
        )

        if not file_path:
            return ""

        folder_dir = os.path.dirname(file_path)
        employee_names = []

        # Step 2: Extract employee names from names.csv
        try:
            with open(file_path, mode="r", encoding="utf-8") as f:
                reader = csv.reader(f)
                header = next(reader, None)  # Skip header row if present ('EmployeeName')
                for row in reader:
                    if row and row[0].strip():
                        # If header wasn't 'EmployeeName', include first row data
                        if header and header[0] != "EmployeeName":
                            employee_names.append(header[0].strip())
                            header = None
                        employee_names.append(row[0].strip())
        except Exception as e:
            print(f"Error reading names.csv: {e}")
            return ""

        all_text_chunks = []

        # Step 3: Loop through each employee's schedule CSV file
        for name in employee_names:
            emp_csv_path = os.path.join(folder_dir, f"{name}.csv")

            if os.path.exists(emp_csv_path):
                with open(emp_csv_path, mode="r", encoding="utf-8") as emp_file:
                    reader = csv.reader(emp_file)
                    for row in reader:
                        for field in row:
                            # Remove all spaces/whitespace from every cell text
                            clean_field = "".join(str(field).split())
                            all_text_chunks.append(clean_field)

        # Step 4: Concatenate all text into a single string with no spaces
        combined_result = "".join(all_text_chunks)

        if not root_exists:
            root_win.destroy()

        return combined_result

    def scan_folders(self):
        schedule_data_string = self.get_root()
        self.make_coin(schedule_data_string)

    def save_coins(self, block_data: Dict[str, Any]):
        self.coins.append(block_data)
        if 'coin_cloud' in globals():
            coin_cloud.save(self.coins)
