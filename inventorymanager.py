#Project: The "86-List" Inventory Manager
#Focus: Learning to use models. Added a validator.py

import sys
from datetime import datetime
# Import our specialized validators
from validator import get_int

# ==========================================
# PHASE 1: THE SETUP (THE "BRAIN")
# ==========================================

# 1. CUSTOM ERROR
# We create a special name "InventoryError" so the computer knows 
# specifically when our kitchen math doesn't make sense.
class InventoryError(Exception):
    #Exception raised when physical count is higher than calculated stock.
    pass

def main():
    # 2. DATE & TIME HEADER
    # This section creates a professional timestamp for the shift manager.
    try:
        now = datetime.now()
        day = now.day
        # Logic to add 'st', 'nd', 'rd', or 'th' to the date
        suffix = "th" if 11 <= day <= 13 else {1: "st", 2: "nd", 3: "rd"}.get(day % 10, "th")
        formatted_date = now.strftime(f"%A, %B {day}{suffix}, at %I:%M %p")
        print(f"\n--- Inventory Report for {formatted_date} ---")
        print("💡 Tip: Just press ENTER if the count is 0.")
    except Exception:
        # Fallback if the date logic fails
        print("\n--- End of Shift Inventory Report ---")

    # 3. DATA STRUCTURE: List of Dictionaries
    # Each dictionary holds the 'Static' data (costs and pars) for a product.
    # unit_price: The price we charge the customer for one item.
    # par_level: The target amount we want to have in stock.
    inventory = [
        {"name": "Burgers", "line_inv": 10, "walk_in_inv": 5, "freezer_inv": 5, "unit_price": 18.00, "par_level": 20},
        {"name": "Cornish Hens", "line_inv": 10, "walk_in_inv": 5, "freezer_inv": 5, "unit_price": 26.00, "par_level": 20},
        {"name": "Crabcakes", "line_inv": 10, "walk_in_inv": 5, "freezer_inv": 5, "unit_price": 21.00, "par_level": 20},
        {"name": "Elotes", "line_inv": 10, "walk_in_inv": 5, "freezer_inv": 5, "unit_price": 15.00, "par_level": 20},
        {"name": "Lamb Chops", "line_inv": 10, "walk_in_inv": 5, "freezer_inv": 5, "unit_price": 28.00, "par_level": 20},
        {"name": "Pork Chops", "line_inv": 10, "walk_in_inv": 5, "freezer_inv": 5, "unit_price": 29.00, "par_level": 20},
        {"name": "Ribeye Steak", "line_inv": 10, "walk_in_inv": 5, "freezer_inv": 5, "unit_price": 38.00, "par_level": 20},
        {"name": "Rustic Bread", "line_inv": 10, "walk_in_inv": 5, "freezer_inv": 5, "unit_price": 12.00, "par_level": 20},
        {"name": "Salmon", "line_inv": 10, "walk_in_inv": 5, "freezer_inv": 5, "unit_price": 36.00, "par_level": 20},
        {"name": "Scallops", "line_inv": 10, "walk_in_inv": 5, "freezer_inv": 5, "unit_price": 38.00, "par_level": 20}
    ]

   # INITIAL MATH LOOP
    # Pre-calculate the starting totals before the shift begins
    for p in inventory:
        # Add Line and Walk-in stock to see what we use daily
        p["daily_usage"] = p["line_inv"] + p["walk_in_inv"]
        # Total stock is everything combined (including freezer)
        p["starting_inv"] = p["daily_usage"] + p["freezer_inv"]

    # ==========================================
    # PHASE 2: THE SHIFT DATA (THE "INPUT")
    # ==========================================

    # This list will hold details of any missing items we find
    shrinkage_list = []
    waste_list = []

    # --- PHASE 2: THE INPUT ---
    for p in inventory:
        # While True keeps asking the same item until the user gives valid numbers
        while True: 
            try:
                print(f"\n📝 RECORDING: {p['name'].upper()}")
                # Ask the user for three specific numbers
                # allow_zero=True means hitting 'Enter' or '0' is valid
                sold = get_int(f"  How many {p['name']} sold? ", allow_zero=True)
                comps = get_int(f"  How many {p['name']} were waste/comps? ", allow_zero=True)
                count = get_int(f"  What is the final physical count for {p['name']}? ", allow_zero=True)



                # NEW: FAT FINGER GUARDRAIL - Verification for high numbers
                if sold > 50 or comps > 50 or count > 50:
                    confirm = input(f"  ⚠️  {max(sold, comps, count)} seems high for {p['name']}. Correct? (y/n): ").lower()
                    if confirm != 'y':
                        print(f"  🔄 Restarting entry for {p['name']}...")
                        continue

                # If the user typed a negative number or letters, show an error
                if sold < 0 or comps < 0 or count < 0:
                    print(f"  ❌ Error: Numbers must be positive for {p['name']}.")
                    continue

                # Math: What SHOULD be left according to the sales
                expected = p["starting_inv"] - (sold + comps)

                # If count is higher than starting, that's impossible. Trigger Exception.
                if count > expected:
                    raise InventoryError(f"Math Error: You only started with {p['starting_inv']} {p['name']}.")
                
                # Calculate how much money we made from this item
                item_sales_val = sold * p["unit_price"]

                # If the shelf count is lower than expected, we have "Shrinkage"
                if count < expected:
                    missing = expected - count
                    loss_val = missing * p["unit_price"]
                    # Add to our list for the final report
                    shrinkage_list.append({"name": p['name'], "qty": missing, "loss": loss_val, "base_sales": item_sales_val})
                    print(f"  ⚠️  ALERT: {missing} {p['name']} missing (${loss_val:.2f} lost).")
                
                # If we recorded comps (waste), add it to the waste log
                if comps > 0:
                    waste_val = comps * p["unit_price"]
                    waste_list.append({"name": p['name'], "qty": comps, "loss": waste_val, "base_sales": item_sales_val})

                # Save everything into the main item dictionary
                p.update({"sold": sold, "comps": comps, "final": count, "sales_dollars": item_sales_val})
                # Break the while loop to move to the next item in the inventory list
                break 
            except InventoryError as e:
                # Catch the error we 'raised' and print the message for the user
                print(f"  ❌ {e}")

    # ==========================================
    # PHASE 3: THE REPORTING (THE "OUTPUT")
    # ==========================================
    # call the helper function to print everything out
    print_final_reports(inventory, shrinkage_list, waste_list)
    total_net_sales = sum(p["sales_dollars"] for p in inventory)
    return total_net_sales



def print_final_reports(inventory, shrinkage_list, waste_list):
    """
    Helper function to handle all the complex reporting and table formatting.
    This separates the 'Action' of the shift from the 'Result' of the report.
    """
    total_net_sales = sum(p["sales_dollars"] for p in inventory)
    total_comp_value = 0
    prep_list = []
    shopping_list = []
    eighty_six_list = []

    # Print the Main Performance Table
    print("\n" + "="*95)
    print(f"{'PRODUCT':<15} | {'STOCK':>6} | {'STATUS':<15} | {'SALES $':>10} | {'% OF TOTAL SALES'}")
    print("-" * 95)

    for p in inventory:
        total_comp_value += (p["comps"] * p["unit_price"])
        item_pct = (p["sales_dollars"] / total_net_sales * 100) if total_net_sales > 0 else 0
        
        if p["final"] == 0:
            status, color = "86-OUT", "🔴"
            eighty_six_list.append(p["name"].upper())
        elif p["final"] <= (p["par_level"] * 0.25): status, color = "CRITICAL", "🟡"
        elif p["final"] <= (p["par_level"] * 0.5): status, color = "LOW", "🟡"
        else: status, color = "OK", "🟢"

        print(f"{p['name']:<15} | {p['final']:>6} | {color} {status:<12} | ${p['sales_dollars']:>9.2f} | {item_pct:>13.1f}%")

        to_order = p["par_level"] - p["final"]
        if p["final"] <= (p["daily_usage"] * 0.5): 
            prep_list.append({"name": p["name"], "qty": to_order})
        if p["final"] <= (p["par_level"] * 0.25): 
            shopping_list.append({"name": p["name"], "qty": to_order})

    # Shrinkage Report
    print("\n" + "="*75)
    print(f"{'SHRINKAGE BREAKDOWN':<25} | {'QTY':>5} | {'LOSS $':>10} | {'% OF ITEM SALES'}")
    print("-" * 75)
    total_shrink_loss = sum(s['loss'] for s in shrinkage_list)
    for s in shrinkage_list:
        s_pct = (s['loss'] / s['base_sales'] * 100) if s['base_sales'] > 0 else 100.0
        print(f"{s['name']:<25} | {s['qty']:>5} | ${s['loss']:>9.2f} | {s_pct:>14.1f}%")
    if not shrinkage_list: print("No shrinkage detected.")

    # Waste Log
    print("\n" + "="*75)
    print(f"{'WASTE LOG (COMPS)':<25} | {'QTY':>5} | {'LOSS $':>10} | {'% OF ITEM SALES'}")
    print("-" * 75)
    for w in waste_list:
        w_pct = (w['loss'] / w['base_sales'] * 100) if w['base_sales'] > 0 else 100.0
        print(f"{w['name']:<25} | {w['qty']:>5} | ${w['loss']:>9.2f} | {w_pct:>14.1f}%")
    if not waste_list: print("No recorded waste.")

    # Financial Summary
    potential_revenue = total_net_sales + total_comp_value + total_shrink_loss
    shrink_of_total = (total_shrink_loss / total_net_sales * 100) if total_net_sales > 0 else 0
    comp_of_total = (total_comp_value / total_net_sales * 100) if total_net_sales > 0 else 0

    print("\n" + "="*55)
    print(f"{'--- NIGHTLY FINANCIAL SUMMARY ---':^55}")
    print("-" * 55)
    print(f"TOTAL NET SALES (SOLD):         ${total_net_sales:>12.2f}")
    print(f"TOTAL COMP VALUE (% OF SALES):  ${total_comp_value:>12.2f} ({comp_of_total:>5.1f}%)")
    print(f"TOTAL SHRINKAGE LOSS (%):       ${total_shrink_loss:>12.2f} ({shrink_of_total:>5.1f}%)")
    print("-" * 55)
    print(f"TOTAL POTENTIAL REVENUE:        ${potential_revenue:>12.2f}")
    print("="*55)

    # Kitchen Lists
    print(f"\n🚨 86 LIST: {', '.join(eighty_six_list) if eighty_six_list else 'NONE'}")
    
    print("\n" + "="*45)
    print(f"{'KITCHEN PREP LIST':<30} | {'QTY':>5}")
    print("-" * 45)
    for i in prep_list: print(f"{i['name']:<30} | {i['qty']:>5}")

    print("\n" + "="*45)
    print(f"{'MANAGER SHOPPING LIST':<30} | {'QTY':>5}")
    print("-" * 45)
    for i in shopping_list: print(f"{i['name']:<30} | {i['qty']:>5}")


if __name__ == "__main__":
    main()
