import pandas as pd
from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import FileUploadForm, TaxForm, GoalForm
from .models import UploadedFile, Goal
import os
import openai
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from io import BytesIO
import base64
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm







# Federal and State tax data
SINGLE_BRACKETS = [
    (0, 11925, 0.10), (11926, 48475, 0.12), (48476, 103350, 0.22),
    (103351, 197300, 0.24), (197301, 250525, 0.32), (250526, 626350, 0.35),
    (626351, float('inf'), 0.37),
]
MARRIED_BRACKETS = [
    (0, 23850, 0.10), (23851, 96950, 0.12), (96951, 206700, 0.22),
    (206701, 413550, 0.24), (413551, 523050, 0.32), (523051, 1252700, 0.35),
    (1252701, float('inf'), 0.37),
]
STANDARD_DEDUCTIONS = {'single': 15750, 'married': 31500}
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





def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('dashboard')
        else:
            messages.error(request, 'Invalid username or password.')
    else:
        form = AuthenticationForm()
    return render(request, 'finance/login.html', {'form': form})

def logout_view(request):
    logout(request)
    return redirect('login')

def register_view(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=password)
            login(request, user)
            return redirect('dashboard')
        else:
            messages.error(request, 'Error creating account.')
    else:
        form = UserCreationForm()
    return render(request, 'finance/register.html', {'form': form})


STANDARD_DEDUCTIONS = {
    'single': 12950,
    'married_filing_jointly': 25900,
    'head_of_household': 19400,
}



@login_required
def set_goal(request):
    if request.method == 'POST':
        form = GoalForm(request.POST)
        if form.is_valid():
            goal = form.save(commit=False)
            goal.user = request.user
            goal.current_amount = 0.00  # Initialize
            goal.save()
            messages.success(request, 'Goal set successfully!')
            return redirect('dashboard')
    else:
        form = GoalForm()
    return render(request, 'finance/set_goal.html', {'form': form})

def calculate_federal_tax(taxable_income, filing_status):
    # Simplified placeholder - replace with actual tax brackets
    if filing_status == 'single':
        if taxable_income <= 10000: return taxable_income * 0.1
        return 1000 + (taxable_income - 10000) * 0.12
    return taxable_income * 0.12  # Placeholder

def calculate_state_tax(taxable_income, state):
    # Simplified placeholder - replace with state-specific rates
    return taxable_income * 0.03  # 3% state tax

def generate_tax_charts(federal_tax, state_tax, total_tax, effective_rate):
    # Placeholder for chart generation (adapt from previous Matplotlib code)
    from io import BytesIO
    import matplotlib.pyplot as plt
    import base64

    fig_pie, ax_pie = plt.subplots()
    ax_pie.pie([federal_tax, state_tax], labels=['Federal', 'State'], autopct='%1.1f%%', colors=['#ff6384', '#36a2eb'])
    ax_pie.set_title('Tax Distribution')
    buffer_pie = BytesIO()
    fig_pie.savefig(buffer_pie, format='png')
    buffer_pie.seek(0)
    pie_b64 = base64.b64encode(buffer_pie.getvalue()).decode()
    plt.close(fig_pie)

    fig_bar, ax_bar = plt.subplots()
    ax_bar.bar(['Total Tax', 'Effective Rate'], [total_tax, effective_rate], color=['#ffce56', '#4bc0c0'])
    ax_bar.set_title('Tax Overview')
    buffer_bar = BytesIO()
    fig_bar.savefig(buffer_bar, format='png')
    buffer_bar.seek(0)
    bar_b64 = base64.b64encode(buffer_bar.getvalue()).decode()
    plt.close(fig_bar)

    return pie_b64, bar_b64

def generate_tax_charts(federal_tax, state_tax, total_tax, effective_rate):
    """Generate Matplotlib pie and bar charts as base64 images."""
    fig1, ax1 = plt.subplots()
    ax1.pie([federal_tax, state_tax], labels=['Federal Tax', 'State Tax'], autopct='%1.1f%%', colors=['#ff6384', '#36a2eb'])
    ax1.set_title('Tax Breakdown')
    pie_buffer = BytesIO()
    fig1.savefig(pie_buffer, format='png')
    pie_buffer.seek(0)
    pie_b64 = base64.b64encode(pie_buffer.getvalue()).decode()
    plt.close(fig1)

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

def generate_spending_chart(df):
    try:
        if 'Category' in df.columns and 'Amount' in df.columns:
            category_totals = df.groupby('Category')['Amount'].sum()
            if category_totals.empty:
                print("No data to chart.")
                return None
            fig, ax = plt.subplots()
            ax.pie(
                category_totals,
                labels=category_totals.index,
                autopct='%1.1f%%',
                colors=['#ff6384', '#36a2eb', '#ffce56', '#4bc0c0', '#9966ff']
            )
            ax.set_title('Spending by Category')
            buffer = BytesIO()
            fig.savefig(buffer, format='png')
            buffer.seek(0)
            chart_b64 = base64.b64encode(buffer.getvalue()).decode()
            plt.close(fig)
            print(f"Chart generated with {len(category_totals)} categories.")
            return chart_b64
        else:
            print("Missing Category or Amount columns.")
            return None
    except Exception as e:
        print(f"Chart generation error: {e}")
        return None

@login_required
def upload_file(request):
    if request.method == 'POST':
        form = FileUploadForm(request.POST, request.FILES)
        if form.is_valid():
            uploaded_file = form.save(commit=False)
            uploaded_file.user = request.user
            uploaded_file.save()
            chart = None
            summary = "No summary available"
            file_path = uploaded_file.file.path
            print(f"Saved file path: {file_path}")
            if not os.path.exists(file_path):
                raise FileNotFoundError(f"File not found at {file_path}")
            try:
                if file_path.endswith('.csv'):
                    df = pd.read_csv(file_path)
                    print(f"CSV columns: {df.columns.tolist()}")
                    if 'Category' in df.columns and 'Amount' in df.columns:
                        content = df.to_string()
                        try:
                            api_key = os.getenv('OPENAI_API_KEY')
                            if not api_key:
                                raise Exception("API key missing")
                            openai.api_key = api_key
                            prompt = f"""You are an expert finance analyst AI.
                            Analyze the given financial data and provide:
                            - Total income, total expenses, and savings
                            - Top 3 spending categories
                            - Short advice on reducing unnecessary spending
                            - General financial health summary
                            Output in plain text, not JSON.
                            Data: {content[:4000]}"""
                            response = openai.ChatCompletion.create(
                                model="gpt-3.5-turbo",
                                messages=[
                                    {"role": "system", "content": "You are a helpful finance assistant."},
                                    {"role": "user", "content": prompt}
                                ]
                            )
                            summary = response.choices[0].message.content
                        except Exception as e:
                            messages.warning(request, f"AI analysis unavailable (quota issue?): {str(e)}. Showing basic analysis instead.")
                            summary = "AI analysis unavailable due to quota limits. Tip: Review high-spending categories to optimize budget."
                        chart = generate_spending_chart(df)
                    else:
                        messages.warning(request, "CSV must have 'Category' and 'Amount' columns for chart.")
                uploaded_file.summary = summary
                uploaded_file.save()
                messages.success(request, 'File uploaded and analyzed!')
                return render(request, 'finance/result.html', {
                    'summary': summary,
                    'chart': chart,
                    'file_id': uploaded_file.id
                })
            except Exception as e:
                messages.error(request, f"Error processing file: {str(e)}")
                uploaded_file.summary = summary
                uploaded_file.save()
                return redirect('upload')
    else:
        form = FileUploadForm()
    return render(request, 'finance/upload.html', {'form': form})
@login_required
def dashboard(request):
    latest_file = UploadedFile.objects.filter(user=request.user).order_by('-created_at').first()
    latest_summary = latest_file.summary if latest_file else "No files uploaded yet."
    pie_data = {'labels': ['Food', 'Rent', 'Utilities', 'Travel', 'Entertainment'], 'data': [140, 700, 140, 225, 25]}
    chart = None
    goal_progress = 0
    ai_message = "Keep up the good work on your financial goals!"

    if latest_file and latest_file.file.path.endswith('.csv'):
        try:
            file_path = latest_file.file.path
            df = pd.read_csv(file_path)
            print(f"Dashboard CSV columns: {df.columns.tolist()}")
            if 'Category' in df.columns and 'Amount' in df.columns:
                category_totals = df.groupby('Category')['Amount'].sum().to_dict()
                pie_data = {'labels': list(category_totals.keys()), 'data': list(category_totals.values())}
                chart = generate_spending_chart(df)
                # Calculate progress for the latest goal
                latest_goal = Goal.objects.filter(user=request.user).order_by('-created_at').first()
                if latest_goal and 'Credit' in df.columns:  # Adjust 'Credit' based on your CSV
                    total_savings = df[df['Category'] == 'Savings']['Amount'].sum() if 'Savings' in df['Category'].values else 0
                    goal_progress = min(100, (total_savings / latest_goal.target_amount) * 100) if latest_goal.target_amount > 0 else 0
                    try:
                        openai.api_key = os.getenv('OPENAI_API_KEY')
                        prompt = f"Encourage a user saving for '{latest_goal.title}' with ${total_savings} of ${latest_goal.target_amount} saved. Provide a concise, motivational message."
                        response = openai.ChatCompletion.create(model="gpt-3.5-turbo", messages=[{"role": "user", "content": prompt}])
                        ai_message = response.choices[0].message.content
                    except Exception:
                        ai_message = "Great effort! Keep tracking your savings to hit your goal!"
            else:
                print("Missing Category or Amount columns in dashboard data.")
        except Exception as e:
            print(f"Dashboard CSV error: {e}")
            messages.warning(request, f"Could not load file data: {str(e)}.")

    print(f"Dashboard rendering with username: {request.user.username}, summary: {latest_summary}, chart: {chart is not None}, goal_progress: {goal_progress}%")
    return render(request, 'finance/dashboard.html', {
        'pie_data': pie_data,
        'latest_summary': latest_summary,
        'chart': chart,
        'username': request.user.username,
        'goal_progress': goal_progress,
        'ai_message': ai_message,
    })
@login_required
def result(request, file_id):
    uploaded_file = UploadedFile.objects.get(id=file_id)
    chart = None
    if uploaded_file.file.path.endswith('.csv'):
        try:
            df = pd.read_csv(uploaded_file.file.path)
            chart = generate_spending_chart(df)
        except Exception as e:
            print(f"Error generating chart for result: {e}")
    return render(request, 'result.html', {
        'summary': uploaded_file.summary,
        'chart': chart
    })
@login_required
def tax_calculator(request):
    ai_advice = None
    charts = None
    if request.method == 'POST':
        form = TaxForm(request.POST)
        if form.is_valid():
            gross_income = float(form.cleaned_data['gross_income'])
            filing_status = form.cleaned_data['filing_status']
            state = form.cleaned_data['state']
            deductions = float(form.cleaned_data['deductions']) if form.cleaned_data['deductions'] else 0
            std_deduction = STANDARD_DEDUCTIONS[filing_status]
            total_deductions = max(deductions, std_deduction)
            taxable_income = max(0, gross_income - total_deductions)
            federal_tax = calculate_federal_tax(taxable_income, filing_status)
            state_tax = calculate_state_tax(taxable_income, state)
            total_tax = federal_tax + state_tax
            effective_rate = round((total_tax / gross_income) * 100, 1) if gross_income > 0 else 0

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
                    model="gpt-3.5-turbo",
                    messages=[{"role": "user", "content": prompt}]
                )
                ai_advice = response.choices[0].message.content
                messages.success(request, 'Tax calculated and analyzed!')
            except Exception as e:
                messages.warning(request, f"AI analysis unavailable (quota issue?): {str(e)}. Showing charts instead.")
                pie_b64, bar_b64 = generate_tax_charts(federal_tax, state_tax, total_tax, effective_rate)
                charts = {'pie': pie_b64, 'bar': bar_b64}
                ai_advice = "AI temporarily unavailable—check billing. Tip: Max retirement contributions to lower taxable income!"

            return render(request, 'finance/tax_calculator.html', {
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
                'charts': charts,
            })
    else:
        form = TaxForm()
    return render(request, 'finance/tax_calculator.html', {'form': form})