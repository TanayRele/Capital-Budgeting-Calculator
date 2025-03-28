import tkinter as tk
from tkinter import messagebox, ttk
import numpy as np
import numpy_financial as npf

# Function to calculate Payback Period
def calculate_payback():
    try:
        investment = float(entry_investment.get())
        cash_flows = list(map(float, entry_cash_flows.get().split(',')))
        tax_rate = float(entry_tax_rate.get()) / 100  # Convert percentage to decimal
        cf_after_tax = [cf * (1 - tax_rate) for cf in cash_flows]

        cumulative_cash_flow = 0
        payback_period = 0
        for i, cf in enumerate(cf_after_tax):
            cumulative_cash_flow += cf
            if cumulative_cash_flow >= investment:
                payback_period = i + 1
                break

        if payback_period == 0:
            result_text = "Payback Period: Not achieved within the provided cash flows."
            label_payback.config(text=result_text, fg="#8B0000")
        else:
            result_text = f"Payback Period: {payback_period} years"
            label_payback.config(text=result_text, fg="#006400")
    except ValueError:
        messagebox.showerror("Input Error", "Please enter valid numerical values for Investment, Cash Flows, and Tax Rate.")

# Function to calculate ARR
def calculate_arr():
    try:
        investment = float(entry_investment.get())
        cash_flows = list(map(float, entry_cash_flows.get().split(',')))
        tax_rate = float(entry_tax_rate.get()) / 100
        cf_after_tax = [cf * (1 - tax_rate) for cf in cash_flows]

        avg_profit = np.mean(cf_after_tax)
        arr = (avg_profit / investment) * 100
        label_arr.config(text=f"ARR: {arr:.2f}%", fg="#00008B")
    except ValueError:
        messagebox.showerror("Input Error", "Please enter valid numerical values for Investment, Cash Flows, and Tax Rate.")

# Function to calculate NPV, PI, IRR and Discounted Payback Period
def calculate_dcf():
    try:
        investment = float(entry_investment.get())
        cash_flows = list(map(float, entry_cash_flows.get().split(',')))
        discount_rate = float(entry_discount_rate.get())
        tax_rate = float(entry_tax_rate.get()) / 100
        cf_after_tax = [cf * (1 - tax_rate) for cf in cash_flows]

        discounted_cash_flows = []
        npv = -investment
        for i, cf in enumerate(cf_after_tax):
            discounted_cf = cf / (1 + discount_rate / 100) ** (i + 1)
            discounted_cash_flows.append(discounted_cf)
            npv += discounted_cf

        pi = (npv + investment) / investment  # Corrected PI calculation
        irr_result = npf.irr([-investment] + cf_after_tax)
        irr = irr_result * 100 if irr_result is not None else float('nan')

        # Calculate Discounted Payback Period
        cumulative_discounted_cash_flow = 0
        discounted_payback_period = 0
        for i, dcf in enumerate(discounted_cash_flows):
            cumulative_discounted_cash_flow += dcf
            if cumulative_discounted_cash_flow >= investment:
                # Linear interpolation for more precise period
                excess = cumulative_discounted_cash_flow - investment
                previous_cumulative = cumulative_discounted_cash_flow - dcf
                fraction = (investment - previous_cumulative) / dcf
                discounted_payback_period = i + fraction + 1  # +1 because enumerate starts at 0
                break
        if cumulative_discounted_cash_flow < investment:
            discounted_payback_period = "Not achieved within the provided cash flows."

        # Update main result labels
        if isinstance(discounted_payback_period, float):
            dpb_text = f"{discounted_payback_period:.2f} years"
        else:
            dpb_text = discounted_payback_period

        result_text = f"NPV: {npv:.2f}\nPI: {pi:.2f}\nIRR: {irr:.2f}%\nDiscounted Payback Period: {dpb_text}"
        label_result.config(text=result_text, fg="#8B0000")

        # Display discounted cash flows in a new window
        display_dcf(cash_flows, cf_after_tax, discounted_cash_flows)
    except ValueError:
        messagebox.showerror("Input Error", "Please enter valid numerical values for Investment, Cash Flows, Discount Rate, and Tax Rate.")
    except Exception as e:
        messagebox.showerror("Calculation Error", f"An error occurred: {e}")

# Function to display Discounted Cash Flows
def display_dcf(pre_tax_cf, cf_after_tax, discounted_cash_flows):
    dcf_window = tk.Toplevel(root)
    dcf_window.title("Discounted Cash Flows")
    
    # Create a frame with scrollbar
    main_frame = ttk.Frame(dcf_window)
    main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
    
    # Create canvas and scrollbar
    canvas = tk.Canvas(main_frame)
    scrollbar = ttk.Scrollbar(main_frame, orient="vertical", command=canvas.yview)
    scrollable_frame = ttk.Frame(canvas)
    
    scrollable_frame.bind(
        "<Configure>",
        lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
    )
    
    canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
    canvas.configure(yscrollcommand=scrollbar.set)
    
    # Pack the scrollbar and canvas
    scrollbar.pack(side="right", fill="y")
    canvas.pack(side="left", fill="both", expand=True)
    
    # Configure the window to be resizable
    dcf_window.resizable(True, True)
    
    # Headers
    ttk.Label(scrollable_frame, text="Year", font=("Arial", 12, "bold")).grid(row=0, column=0, padx=10, pady=10)
    ttk.Label(scrollable_frame, text="Pre-Tax Cash Flow", font=("Arial", 12, "bold")).grid(row=0, column=1, padx=10, pady=10)
    ttk.Label(scrollable_frame, text="After-Tax Cash Flow", font=("Arial", 12, "bold")).grid(row=0, column=2, padx=10, pady=10)
    ttk.Label(scrollable_frame, text="Discounted Cash Flow", font=("Arial", 12, "bold")).grid(row=0, column=3, padx=10, pady=10)

    # Populate rows
    for i, (pre_cf, aft_cf, dcf) in enumerate(zip(pre_tax_cf, cf_after_tax, discounted_cash_flows), start=1):
        ttk.Label(scrollable_frame, text=f"{i}", font=("Arial", 12)).grid(row=i, column=0, padx=10, pady=5)
        ttk.Label(scrollable_frame, text=f"{pre_cf:.2f}", font=("Arial", 12)).grid(row=i, column=1, padx=10, pady=5)
        ttk.Label(scrollable_frame, text=f"{aft_cf:.2f}", font=("Arial", 12)).grid(row=i, column=2, padx=10, pady=5)
        ttk.Label(scrollable_frame, text=f"{dcf:.2f}", font=("Arial", 12)).grid(row=i, column=3, padx=10, pady=5)

    # Total Discounted Cash Flow
    total_dcf = sum(discounted_cash_flows)
    total_label = ttk.Label(
        scrollable_frame, 
        text=f"Total Discounted Cash Flow: {total_dcf:.2f}", 
        font=("Arial", 12, "bold")
    )
    total_label.grid(row=len(discounted_cash_flows)+1, column=0, columnspan=4, pady=10)

# Function to calculate Cash Flows After Taxes (CFAT)
def calculate_cfat():
    try:
        # Inputs
        depreciable_base = float(entry_depreciable_base.get())
        economic_life = int(entry_economic_life.get())
        ebitda_list = list(map(float, entry_ebitda.get().split(',')))
        tax_rate = float(entry_tax_rate.get()) / 100  # Convert percentage to decimal

        # Check if the number of EBITDA entries matches the economic life
        if len(ebitda_list) != economic_life:
            messagebox.showerror("Input Error", "EBITDA should match the number of economic life years")
            return

        # Calculate annual depreciation (Straight-line method)
        annual_depreciation = depreciable_base / economic_life

        # Clear existing rows in the treeview
        for row in tree.get_children():
            tree.delete(row)

        # Calculate CFAT for each year and populate the treeview
        for year in range(economic_life):
            ebitda = ebitda_list[year]
            taxable_income = ebitda - annual_depreciation
            tax = taxable_income * tax_rate if taxable_income > 0 else 0  # Ensure no negative tax
            net_income = taxable_income - tax
            cfat = net_income + annual_depreciation

            # Append the row to the treeview
            tree.insert('', 'end', values=(year + 1, ebitda, annual_depreciation, taxable_income, tax, net_income, annual_depreciation, cfat))

        # Display a message indicating calculation completion
        messagebox.showinfo("Calculation Complete", "CFAT calculated successfully!")

    except ValueError:
        messagebox.showerror("Input Error", "Please enter valid numerical values for all fields.")
    except Exception as e:
        messagebox.showerror("Calculation Error", f"An error occurred: {e}")

# Main application window
root = tk.Tk()
root.title("Investment Analysis Tool")
root.geometry("800x600")
root.configure(bg="#E0F7FA")

# Investment Inputs
tk.Label(root, text="Investment Amount:", bg="#E0F7FA", font=("Arial", 12)).grid(row=0, column=0, padx=10, pady=10)
entry_investment = tk.Entry(root, width=20)
entry_investment.grid(row=0, column=1, padx=10, pady=10)

tk.Label(root, text="Cash Flows (comma-separated):", bg="#E0F7FA", font=("Arial", 12)).grid(row=1, column=0, padx=10, pady=10)
entry_cash_flows = tk.Entry(root, width=20)
entry_cash_flows.grid(row=1, column=1, padx=10, pady=10)

tk.Label(root, text="Tax Rate (%):", bg="#E0F7FA", font=("Arial", 12)).grid(row=2, column=0, padx=10, pady=10)
entry_tax_rate = tk.Entry(root, width=20)
entry_tax_rate.grid(row=2, column=1, padx=10, pady=10)

tk.Label(root, text="Discount Rate (%):", bg="#E0F7FA", font=("Arial", 12)).grid(row=3, column=0, padx=10, pady=10)
entry_discount_rate = tk.Entry(root, width=20)
entry_discount_rate.grid(row=3, column=1, padx=10, pady=10)

# Calculate Buttons
tk.Button(root, text="Calculate Payback Period", command=calculate_payback, bg="#81D4FA").grid(row=4, column=0, padx=10, pady=10)
tk.Button(root, text="Calculate ARR", command=calculate_arr, bg="#81D4FA").grid(row=4, column=1, padx=10, pady=10)
tk.Button(root, text="Calculate NPV, PI, IRR, Discounted Payback", command=calculate_dcf, bg="#81D4FA").grid(row=5, column=0, padx=10, pady=10, columnspan=2)

# Results Labels
label_payback = tk.Label(root, text="", bg="#E0F7FA", font=("Arial", 12, "bold"))
label_payback.grid(row=6, column=0, columnspan=2, pady=10)
label_arr = tk.Label(root, text="", bg="#E0F7FA", font=("Arial", 12, "bold"))
label_arr.grid(row=7, column=0, columnspan=2, pady=10)
label_result = tk.Label(root, text="", bg="#E0F7FA", font=("Arial", 12, "bold"))
label_result.grid(row=8, column=0, columnspan=2, pady=10)

# Add a heading above the depreciable input fields
tk.Label(root, text="Project Cash Flows", bg="#E0F7FA", font=("Arial", 14, "bold")).grid(row=9, column=0, columnspan=2, pady=10)

# Cash Flows After Taxes Inputs for CFAT calculation
tk.Label(root, text="Depreciable Base:", bg="#E0F7FA", font=("Arial", 12)).grid(row=10, column=0, padx=10, pady=10)
entry_depreciable_base = tk.Entry(root, width=20)
entry_depreciable_base.grid(row=10, column=1, padx=10, pady=10)

tk.Label(root, text="Expected Economic Life (years):", bg="#E0F7FA", font=("Arial", 12)).grid(row=11, column=0, padx=10, pady=10)
entry_economic_life = tk.Entry(root, width=20)
entry_economic_life.grid(row=11, column=1, padx=10, pady=10)

tk.Label(root, text="EBITDA (comma-separated):", bg="#E0F7FA", font=("Arial", 12)).grid(row=12, column=0, padx=10, pady=10)
entry_ebitda = tk.Entry(root, width=20)
entry_ebitda.grid(row=12, column=1, padx=10, pady=10)

# Button to calculate Cash Flows After Taxes
tk.Button(root, text="Calculate CFAT", command=calculate_cfat, bg="#81D4FA").grid(row=13, column=0, columnspan=2, pady=10)

# Treeview for CFAT results
columns = ("Year", "EBITDA", "D and A", "Taxable Income", "Tax", "Net Income", "Depreciation", "CFAT")
tree = ttk.Treeview(root, columns=columns, show='headings')
tree.heading("Year", text="Year")
tree.heading("EBITDA", text="EBITDA")
tree.heading("D and A", text="D and A")
tree.heading("Taxable Income", text="Taxable Income")
tree.heading("Tax", text="Tax")
tree.heading("Net Income", text="Net Income")
tree.heading("Depreciation", text="Depreciation")
tree.heading("CFAT", text="CFAT")
for col in columns:
    tree.heading(col, text=col)
    tree.column(col, anchor='center')
tree.grid(row=14, column=0, columnspan=2, padx=10, pady=10)

# Start the GUI loop
root.mainloop()
