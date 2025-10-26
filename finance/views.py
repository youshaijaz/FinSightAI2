import pandas as pd
from openai import OpenAI
from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import FileUploadForm,TaxForm
from .models import UploadedFile
import os
from django.conf import settings
import matplotlib
matplotlib.use('Agg')  # Non-interactive backend for server
import matplotlib.pyplot as plt
from io import BytesIO
import base64





SINGLE_BRACKETS = [
    (0, 11925, 0.10),
    (11926, 48475, 0.12),
    (48476, 103350, 0.22),
    (103351, 197300, 0.24),
    (197301, 250525, 0.32),
    (250526, 626350, 0.35),
    (626351, float('inf'), 0.37),
]


MARRIED_BRACKETS = [
    (0, 23850, 0.10),
    (23851, 96950, 0.12),
    (96951, 206700, 0.22),
    (206701, 413550, 0.24),
    (413551, 523050, 0.32),
    (523051, 1252700, 0.35),
    (1252701, float('inf'), 0.37),
]

# 2025 Standard Deductions
STANDARD_DEDUCTIONS = {
    'single': 15750,
    'married': 31500,
}

STATE_RATES = {
    'CA': 0.093, 'NY': 0.0685, 'TX': 0.0, 'FL': 0.0, 'WA': 0.0,
    'AL': 0.05, 'AK': 0.0, 'AZ': 0.025, 'AR': 0.049, 'CO': 0.044,
    'CT': 0.0699, 'DE': 0.068, 'GA': 0.059, 'HI': 0.11, 'ID': 0.059,
    'IL': 0.0495, 'IN': 0.0315, 'IA': 0.059, 'KS': 0.0575, 'KY': 0.05,
    'LA': 0.0425, 'ME': 0.079, 'MD': 0.0575, 'MA': 0.05, 'MI': 0.0425,
    'MN': 0.0965, 'MS': 0.05, 'MO': 0.0425, 'MT': 0.063, 'NE': 0.0684,
    'NV': 0.0, 'NH': 0.05, 'NJ': 0.0897, 'NM': 0.0599, 'NC': 0.0475,
    'ND': 0.029, 'OH': 0.0379, 'OK': 0.049, 'OR': 0.099, 'PA': 0.0307,
    'RI': 0.0599, 'SC': 0.07, 'SD': 0.0, 'TN': 0.0, 'UT': 0.0465,
    'VT': 0.0895, 'VA': 0.0575, 'WV': 0.065, 'WI': 0.077, 'WY': 0.0,
    'DC': 0.0875,
}

def calculate_federal_tax(taxable_income, filing_status):
    if filing_status == 'single':
        brackets = SINGLE_BRACKETS
    else:
        brackets = MARRIED_BRACKETS
    tax = 0
    prev_upper = 0
    for lower, upper, rate in brackets:
        if taxable_income > prev_upper:
            taxable_in_bracket = min(taxable_income, upper) - max(prev_upper, lower) + 1
            tax += taxable_in_bracket * rate
        prev_upper = upper
    return round(tax, 2)

def calculate_state_tax(taxable_income, state):
    rate = STATE_RATES.get(state, 0.05)
    return round(taxable_income * rate, 2)

def upload_file(request):
    if request.method == 'POST':
        form = FileUploadForm(request.POST, request.FILES)
        if form.is_valid():
            uploaded_file = UploadedFile(file=request.FILES['file'])
            uploaded_file.save()
            file_path = uploaded_file.file.path
            try:
                if file_path.endswith('.csv'):
                    df = pd.read_csv(file_path)
                    content = df.to_string()
                elif file_path.endswith('.xlsx'):
                    df = pd.read_excel(file_path)
                    content = df.to_string()
                else:
                    with open(file_path, 'r') as f:
                        content = f.read()
            except Exception as e:
                messages.error(request, f"Error reading file: {str(e)}")
                return redirect('upload')
            try:
                api_key = os.getenv('OPENAI_API_KEY')
                if not api_key:
                    messages.error(request, "OpenAI API key is missing.")
                    return redirect('upload')
                client = OpenAI(api_key=api_key)
                prompt = f"""You are an expert finance analyst AI.
                Analyze the given financial data and provide:
                - Total income, total expenses, and savings
                - Top 3 spending categories
                - Short advice on reducing unnecessary spending
                - General financial health summary
                Output in plain text, not JSON.
                Data: {content[:4000]}"""
                response = client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[
                        {"role": "system", "content": "You are a helpful finance assistant."},
                        {"role": "user", "content": prompt}
                    ]
                )
                summary = response.choices[0].message.content
                uploaded_file.summary = summary
                uploaded_file.save()
                messages.success(request, 'File uploaded and analyzed!')
                return redirect('result', file_id=uploaded_file.id)
            except Exception as e:
                messages.error(request, f"Error analyzing file with AI: {str(e)}")
                return redirect('upload')
    else:
        form = FileUploadForm()
    return render(request, 'upload.html', {'form': form})



def upload_file(request):
    if request.method == 'POST':
        form = FileUploadForm(request.POST, request.FILES)
        if form.is_valid():
            uploaded_file = UploadedFile(file=request.FILES['file'])
            uploaded_file.save()
            
            # Read file content with Pandas
            file_path = uploaded_file.file.path
            try:
                if file_path.endswith('.csv'):
                    df = pd.read_csv(file_path)
                    content = df.head(500).to_string()
                elif file_path.endswith('.xlsx'):
                    df = pd.read_excel(file_path)
                    content = df.to_string()
                else:  # TXT or LOG
                    with open(file_path, 'r') as f:
                        content = f.read()
            except Exception as e:
                messages.error(request, f"Error reading file: {str(e)}")
                return redirect('upload')
            
            # AI Analysis
            try:
                client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
                prompt = f"""You are an expert finance analyst AI.
                Analyze the given financial data and provide:
                - Total income, total expenses, and savings
                - Top 3 spending categories
                - Short advice on reducing unnecessary spending
                - General financial health summary
                Output in plain text, not JSON.

                Data: {content[:4000]}"""
                
                response = client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[
                        {"role": "system", "content": "You are a helpful finance assistant."},
                        {"role": "user", "content": prompt}
                    ]
                )
                summary = response.choices[0].message.content
                
                uploaded_file.summary = summary
                uploaded_file.save()
                
                messages.success(request, 'File uploaded and analyzed!')
                return redirect('result', file_id=uploaded_file.id)
            except Exception as e:
                messages.error(request, f"Error analyzing file with AI: {str(e)}")
                return redirect('upload')
    else:
        form = FileUploadForm()
    return render(request, 'upload.html', {'form': form})


def result(request, file_id):
    try:
        file_obj = UploadedFile.objects.get(id=file_id)
        return render(request, 'result.html', {'summary': file_obj.summary})
    except UploadedFile.DoesNotExist:
        return redirect('upload')
    

def dashboard(request):
    # Get the latest uploaded file's summary
    latest_file = UploadedFile.objects.order_by('-created_at').first()
    latest_summary = latest_file.summary if latest_file else None
    
    # Mock or parsed pie chart data
    pie_data = {
        'labels': ['Food', 'Rent', 'Utilities', 'Travel'],
        'data': [20, 40, 25, 15]
    }
    
    # Optional: Parse real data from latest CSV
    if latest_file and latest_file.file.path.endswith('.csv'):
        try:
            df = pd.read_csv(latest_file.file.path)
            if 'Category' in df.columns and 'Amount' in df.columns:
                category_totals = df.groupby('Category')['Amount'].sum().to_dict()
                pie_data = {
                    'labels': list(category_totals.keys()),
                    'data': list(category_totals.values())
                }
        except Exception as e:
            print(f"Error parsing CSV: {e}")  # Debug; replace with logging in production
    
    return render(request, 'dashboard.html', {'pie_data': pie_data, 'latest_summary': latest_summary})

def generate_tax_charts(federal_tax, state_tax, total_tax, effective_rate):
    """Generate Matplotlib pie and bar charts as base64 images."""
    # Pie chart: Federal vs State Tax
    fig1, ax1 = plt.subplots()
    ax1.pie([federal_tax, state_tax], labels=['Federal Tax', 'State Tax'], autopct='%1.1f%%', colors=['#ff6384', '#36a2eb'])
    ax1.set_title('Tax Breakdown')
    pie_buffer = BytesIO()
    fig1.savefig(pie_buffer, format='png')
    pie_buffer.seek(0)
    pie_b64 = base64.b64encode(pie_buffer.getvalue()).decode()
    plt.close(fig1)

    # Bar chart: Total Tax vs Effective Rate
    fig2, ax2 = plt.subplots()
    categories = ['Total Tax ($)', 'Effective Rate (%)']
    values = [total_tax, effective_rate]
    ax2.bar(categories, values, color=['#ffce56', '#4bc0c0'])
    ax2.set_title('Tax Summary')
    ax2.set_ylabel('Value')
    bar_buffer = BytesIO()
    fig2.savefig(bar_buffer, format='png')
    bar_buffer.seek(0)
    bar_b64 = base64.b64encode(bar_buffer.getvalue()).decode()
    plt.close(fig2)

    return pie_b64, bar_b64


def tax_calculator(request):
    ai_advice = None
    charts = None
    if request.method == 'POST':
        form = TaxForm(request.POST)
        if form.is_valid():
            gross_income = float(form.cleaned_data['gross_income'])
            filing_status = form.cleaned_data['filing_status']
            state = form.cleaned_data['state']
            deductions = float(form.cleaned_data['deductions']) or 0
            std_deduction = STANDARD_DEDUCTIONS[filing_status]
            total_deductions = max(deductions, std_deduction)
            taxable_income = max(0, gross_income - total_deductions)
            federal_tax = calculate_federal_tax(taxable_income, filing_status)
            state_tax = calculate_state_tax(taxable_income, state)
            total_tax = federal_tax + state_tax
            effective_rate = round((total_tax / gross_income) * 100, 1) if gross_income > 0 else 0

            # AI with fallback
            try:
                api_key = os.getenv('OPENAI_API_KEY')
                if not api_key:
                    raise Exception("API key missing")
                openai.api_key = api_key
                prompt = f"""You are a tax advisor AI. Based on this user's financials:
                - Gross Income: ${gross_income}
                - Filing Status: {filing_status}
                - State: {state}
                - Deductions: ${total_deductions} (includes standard deduction)
                - Taxable Income: ${taxable_income}
                - Estimated Federal Tax: ${federal_tax}
                - Estimated State Tax: ${state_tax}
                - Total Estimated Tax: ${total_tax}
                Provide 3-5 concise, actionable tips to minimize taxes (e.g., retirement contributions, credits). Keep it encouraging and simple. Output in bullet points."""
                response = openai.ChatCompletion.create(
                    model="gpt-3.5-turbo",  # Cheaper model
                    messages=[{"role": "user", "content": prompt}]
                )
                ai_advice = response.choices[0].message.content
                messages.success(request, 'Tax calculated and analyzed!')
            except Exception as e:
                messages.warning(request, f"AI analysis unavailable (quota issue?): {str(e)}. Showing charts instead.")
                # Generate fallback charts
                pie_b64, bar_b64 = generate_tax_charts(federal_tax, state_tax, total_tax, effective_rate)
                charts = {'pie': pie_b64, 'bar': bar_b64}
                ai_advice = "AI temporarily unavailable—check billing. Tip: Max retirement contributions to lower taxable income!"

            return render(request, 'tax_calculator.html', {
                'form': form,
                'results': {
                    'gross_income': gross_income,
                    'taxable_income': taxable_income,
                    'federal_tax': federal_tax,
                    'state_tax': state_tax,
                    'total_tax': total_tax,
                    'effective_rate': effective_rate,
                },
                'ai_advice': ai_advice,
                'charts': charts,  # Pass charts if fallback
            })
    else:
        form = TaxForm()
    return render(request, 'tax_calculator.html', {'form': form})


