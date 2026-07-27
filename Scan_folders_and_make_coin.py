import hashlib
import GeneticChunkGenerator
import csv
import os
from pathlib import Path
from tkinter import filedialog
import tkinter as tk

class handle_Crypto:

    def __init__(self):
        #self.coins = coin_cloud.get_coins() #coin_cloud is reference to the ledger of all available coins. produces [] of coin hashes



    def make_coin(self,text):

        hash_root = coin_cloud.get_root_hash() 
        text += hash_root
        for i in range(200):
            gen = GeneticChunkGenerator.GeneticChunkGenerator()
            gen.get_shas()
	    text+=gen.code
            ggg = gen.generate_population(len(text))
            for ii in range(len(ggg)):
                text += ggg[ii]['genome']

        # 2. Hash the payload to create a short 64-byte fingerprint
        timestamp = int(time.time())
        merkle_root = hashlib.sha512(text.encode()).hexdigest()
        # 3. Mine the Block Header
        nonce = 0
        header_hash = ""
        while not header_hash.startswith("0000"):
            nonce += 1
            # Concatenate header fields WITH the nonce
            header_data = f"{hash_root}:{timestamp}:{merkle_root}:{nonce}"
            header_hash = hashlib.sha512(header_data.encode()).hexdigest() 
     
        self.save_coins(text,header_hash,timestamp,merkle_root,nonce)


    def get_root(self, root_dir=None) -> str:
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
        schedule_data_string = self.get_root(root_dir)
        self.make_coin(schedule_data_string)

    def save_coins(self,text,hash):
        d = {'text':text, 'merkle':self.get_merkle(),'sha':hash}
        self.coins.append(d)
        coin_cloud.save(self.coins)
