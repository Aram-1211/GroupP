// Frontend application logic for the meal tracker dashboard.
const API_BASE = window.location.protocol === 'file:'
    ? 'http://localhost:8000'
    : window.location.origin;
let currentView = 'daily';
let currentTarget = null;
let foods = [];
let weekChart = null;
let currentChartMode = 'calories';
let selectedNutritionGoal = null;

async function refreshFoodOptions(selectedFoodId = null) {
    const foodSelect = document.getElementById('meal-food');
    foodSelect.innerHTML = '';

    try {
        const res = await fetch(`${API_BASE}/api/foods/`);
        if (!res.ok) {
            throw new Error(`HTTP error! status: ${res.status}`);
        }

        foods = await res.json();

        if (foods.length === 0) {
            const opt = document.createElement('option');
            opt.value = '';
            opt.textContent = 'No foods available';
            opt.disabled = true;
            foodSelect.appendChild(opt);
            return;
        }

        foods.forEach(f => {
            const opt = document.createElement('option');
            opt.value = f.id;
            opt.textContent = f.name;
            foodSelect.appendChild(opt);
        });

        if (selectedFoodId !== null) {
            foodSelect.value = selectedFoodId;
        }
    } catch (e) {
        console.error('Cannot load foods:', e);
        const opt = document.createElement('option');
        opt.value = '';
        opt.textContent = 'Error loading foods';
        opt.disabled = true;
        foodSelect.appendChild(opt);
    }
}

function filterFoodOptions() {
    const filterText = document.getElementById('meal-food-search').value.trim().toLowerCase();
    const foodSelect = document.getElementById('meal-food');
    foodSelect.innerHTML = '';

    const matchingFoods = foods.filter(f => f.name.toLowerCase().includes(filterText));

    if (matchingFoods.length === 0) {
        const opt = document.createElement('option');
        opt.value = '';
        opt.textContent = 'No foods found';
        opt.disabled = true;
        foodSelect.appendChild(opt);
        return;
    }

    matchingFoods.forEach(f => {
        const opt = document.createElement('option');
        opt.value = f.id;
        opt.textContent = f.name;
        foodSelect.appendChild(opt);
    });
}

document.addEventListener('DOMContentLoaded', async () => {
    await refreshFoodOptions();

    // Default the meal date to today and prevent selecting future dates.
    const today = new Date().toISOString().split('T')[0];
    const mealDateInput = document.getElementById('meal-date');
    mealDateInput.value = today;
    mealDateInput.max = today;

    // Load the user's macro target and initialize the dashboard.
    await loadTarget();
    await loadDayMeals(new Date());

    // Bind UI controls to actions.
    document.getElementById('btn-daily').addEventListener('click', () => switchView('daily'));
    document.getElementById('btn-weekly').addEventListener('click', () => switchView('weekly'));
    document.getElementById('btn-calories').addEventListener('click', () => switchChartMode('calories'));
    document.getElementById('btn-macronutrients').addEventListener('click', () => switchChartMode('macronutrients'));
    document.getElementById('btn-add-meal').addEventListener('click', () => {
        new bootstrap.Modal(document.getElementById('addMealModal')).show();
    });
    document.getElementById('btn-edit-target').addEventListener('click', () => {
        document.getElementById('target-calories').value = currentTarget.calories;
        document.getElementById('target-protein').value = currentTarget.protein;
        document.getElementById('target-fat').value = currentTarget.fat;
        document.getElementById('target-carbs').value = currentTarget.carbs;
        new bootstrap.Modal(document.getElementById('editTargetModal')).show();
    });
    document.getElementById('add-meal-form').addEventListener('submit', addMeal);
    document.getElementById('custom-meal-form').addEventListener('submit', saveCustomMeal);
    document.getElementById('edit-target-form').addEventListener('submit', updateTarget);
    document.getElementById('meal-food-search').addEventListener('input', filterFoodOptions);

    const showStandardMealFields = () => {
        document.getElementById('standard-meal-fields').style.display = '';
        document.getElementById('custom-meal-fields').style.display = 'none';
    };

    const showCustomMealFields = () => {
        document.getElementById('standard-meal-fields').style.display = 'none';
        document.getElementById('custom-meal-fields').style.display = '';
    };

    document.getElementById('btn-create-custom-meal').addEventListener('click', showCustomMealFields);
    document.getElementById('btn-back-standard-meal').addEventListener('click', showStandardMealFields);

    document.getElementById('addMealModal').addEventListener('show.bs.modal', showStandardMealFields);

    // Nutrition goal selection
    const goalButtons = ['goal-cut', 'goal-maintain', 'goal-bulk'];
    goalButtons.forEach(buttonId => {
        document.getElementById(buttonId).addEventListener('click', () => selectNutritionGoal(buttonId));
    });

    // Weight input changes trigger macro calculation
    document.getElementById('target-weight').addEventListener('input', calculateMacroTargets);

    updateChartModeButtons();
});

async function loadTarget() {
    try {
        const res = await fetch(`${API_BASE}/api/target`);
        currentTarget = await res.json();
    } catch (e) {
        currentTarget = { calories: 2000, protein: 50, fat: 65, carbs: 250 };
    }
    updateMacroSummary();
}

function formatCalories(value) {
    return Math.round(Number(value) || 0);
}

function formatMacro(value) {
    return Number(value || 0).toFixed(1);
}

function updateMacroSummary(totals = null) {
    if (!totals) totals = { calories: 0, protein: 0, fat: 0, carbs: 0 };

    document.getElementById('macro-summary').innerHTML = `
        <div class="macro-item"><span>Calories</span><span><strong>${formatCalories(totals.calories)}</strong> / ${formatCalories(currentTarget.calories)}</span></div>
        <div class="macro-item"><span>Protein</span><span><strong>${formatMacro(totals.protein)}</strong>g / ${formatMacro(currentTarget.protein)}g</span></div>
        <div class="macro-item"><span>Fat</span><span><strong>${formatMacro(totals.fat)}</strong>g / ${formatMacro(currentTarget.fat)}g</span></div>
        <div class="macro-item"><span>Carbs</span><span><strong>${formatMacro(totals.carbs)}</strong>g / ${formatMacro(currentTarget.carbs)}g</span></div>
    `;

    updateNutritionAnalysis(totals);
}

function updateNutritionAnalysis(totals) {
    const panel = document.querySelector('.nutrition-analysis-panel p');
    if (!panel) return;

    const cal = totals.calories || 0;
    const prot = totals.protein || 0;
    const fat = totals.fat || 0;
    const carb = totals.carbs || 0;

    const targetCal = currentTarget.calories;
    const targetProt = currentTarget.protein;
    const targetFat = currentTarget.fat;
    const targetCarb = currentTarget.carbs;

    const advice = [];

    // Empty day
    if (cal === 0) {
        panel.textContent = "A new day. Add meals to begin tracking your nutrition.";
        return;
    }

    // Calories exceeded
    if (cal > targetCal + 150) {
        advice.push(
            "Your calorie intake is above your target today. Consider lower-calorie choices and leaner foods tomorrow to stay on track."
        );
    }

    // Carbs exceeded
    if (carb > targetCarb * 1.15) {
        advice.push(
            "Your carbohydrate intake is higher than your target. Try reducing foods such as rice, bread, pasta, or sugary snacks."
        );
    }

    // Fat exceeded
    if (fat > targetFat * 1.05) {
        advice.push(
            "Your fat intake is above your target. Consider leaner protein choices and using less oil or butter."
        );
    }

    // Protein low while other targets acceptable
    if (
        prot < targetProt * 0.6 &&
        cal <= targetCal + 150 &&
        carb <= targetCarb * 1.15 &&
        fat <= targetFat * 1.05
    ) {
        advice.push(
            "You're partially on track with your nutrition today, but your protein intake could be higher. Try foods such as chicken breast, tuna, eggs, or Greek yogurt."
        );
    }

    // Positive on-track state
    if (
        prot >= targetProt * 0.6 &&
        cal <= targetCal + 150 &&
        carb <= targetCarb * 1.15 &&
        fat <= targetFat * 1.05
    ) {
        advice.push(
            "You're doing well with your nutrition targets today. Keep up the great work."
        );
    }

    panel.textContent =
        advice.length > 0
            ? advice.join(' ')
            : "Keep tracking your meals to see how you align with your nutrition targets.";
}

async function loadDayMeals(day) {
    const dayStr = day.toISOString().split('T')[0];
    try {
        const res = await fetch(`${API_BASE}/api/meals/day/${dayStr}`);
        if (!res.ok) throw new Error('No data');
        const data = await res.json();

        const today = new Date().toISOString().split('T')[0];
        document.getElementById('header-date').textContent =
            dayStr === today ? 'Your Day - Today' : `Your Day - ${dayStr}`;

        updateMacroSummary(data.total);

        const mealsList = document.getElementById('meals-list');
        if (!data.meals.length) {
            mealsList.innerHTML = '<p class="text-muted">No meals recorded for this day.</p>';
            return;
        }

        mealsList.innerHTML = data.meals.map(m => `
                    <div class="meal-item">
    <div class="d-flex justify-content-between">
        <h6>${m.name}</h6>

        <button
            class="btn btn-sm btn-outline-danger"
            onclick="deleteMeal(${m.id})"
        >
            ×
        </button>
    </div>

    <p class="text-muted small mb-0">
        ${m.food_name} - ${m.quantity}g
    </p>

    <small>
        Cal: ${formatCalories(m.calories)}
        | P: ${formatMacro(m.protein)}g
        | F: ${formatMacro(m.fat)}g
        | C: ${formatMacro(m.carbs)}g
    </small>
</div>
                `).join('');
    } catch (e) {
        document.getElementById('meals-list').innerHTML = '<p class="text-muted">Could not load meals.</p>';
    }
}

async function deleteMeal(mealId, selectedDayStr = null) {
    await fetch(`${API_BASE}/api/meals/${mealId}`, { method: 'DELETE' });

    if (currentView === 'weekly' && selectedDayStr) {
        const selectedDay = parseLocalDateString(selectedDayStr);
        const weekStart = new Date(selectedDay);
        weekStart.setDate(selectedDay.getDate() - selectedDay.getDay() + 1);
        await loadWeekStats(weekStart, selectedDayStr);
    } else {
        await loadDayMeals(new Date());
    }
}

async function loadWeekStats(weekStart, selectedDayStr = null) {
    const startStr = getLocalDateString(weekStart);
    try {
        const res = await fetch(`${API_BASE}/api/stats/week/${startStr}`);
        const data = await res.json();

        const endStr = data.week_end;
        document.getElementById('header-date').textContent =
            `Your Week - ${data.week_start} → ${endStr}`;

        const labels = data.daily_stats.map(d => d.day_name);
        const calories = data.daily_stats.map(d => d.calories);
        const protein = data.daily_stats.map(d => d.protein);
        const fat = data.daily_stats.map(d => d.fat);
        const carbs = data.daily_stats.map(d => d.carbs);

        let datasets;
        if (currentChartMode === 'calories') {
            datasets = [
                { label: 'Calories', data: calories, backgroundColor: '#0d6efd' }
            ];
        } else {
            datasets = [
                { label: 'Protein', data: protein.map(p => p * 4), backgroundColor: '#198754', stack: 'macros' },
                { label: 'Fat', data: fat.map(f => f * 9), backgroundColor: '#ffc107', stack: 'macros' },
                { label: 'Carbs', data: carbs.map(c => c * 4), backgroundColor: '#dc3545', stack: 'macros' }
            ];
        }

        if (weekChart) weekChart.destroy();
        const ctx = document.getElementById('week-chart').getContext('2d');
        weekChart = new Chart(ctx, {
            type: 'bar',
            data: {
                labels,
                datasets
            },
            options: {
                responsive: true,
                scales: {
                    x: {
                        beginAtZero: true,
                        ticks: {
                            display: false
                        }
                    },
                    y: {
                        beginAtZero: true,
                        stacked: currentChartMode === 'macronutrients'
                    }
                },
                plugins: {
                    tooltip: {
                        callbacks: {
                            label(context) {
                                const label = context.dataset.label || '';
                                const value = context.parsed?.y ?? context.parsed ?? 0;

                                if (label === 'Protein' || label === 'Fat' || label === 'Carbs') {
                                    let grams;
                                    if (label === 'Protein' || label === 'Carbs') {
                                        grams = value / 4;
                                    } else if (label === 'Fat') {
                                        grams = value / 9;
                                    }
                                    return `${label}: ${formatCalories(value)} kcal (${formatMacro(grams)}g)`;
                                } else {
                                    return `${label}: ${formatCalories(value)}`;
                                }
                            }
                        }
                    }
                },
                onClick: async (e) => {
                    const points = weekChart.getElementsAtEventForMode(e, 'nearest', { intersect: false }, true);

                    if (points.length) {
                        const index = points[0].index;
                        const dayDate = data.daily_stats[index].date;
                        await selectDayByDateString(dayDate);
                    }
                }
            }
        });

        // Render clickable day buttons for the weekly stats view.
        const dayButtonsContainer = document.getElementById('week-day-buttons');
        dayButtonsContainer.innerHTML = data.daily_stats.map((day, index) => `
                    <button 
                        class="btn btn-sm btn-outline-secondary" 
                        data-date="${day.date}"
                        style="padding: 6px 4px; font-size: 0.75rem; width: 100%;"
                        onclick="selectDayByDateString('${day.date}')"
                    >
                        <div>${day.day_name}</div>
                        <small style="display: block; line-height: 1.2;">${day.date}</small>
                    </button>
                `).join('');

        // Select the preserved selected day if provided, otherwise default to today or first day.
        if (selectedDayStr) {
            await selectDayByDateString(selectedDayStr);
        } else {
            const today = getLocalDateString(new Date());
            const todayStats = data.daily_stats.find(d => d.date === today);
            if (todayStats) {
                await selectDayByDateString(todayStats.date);
            } else {
                await selectDayByDateString(data.daily_stats[0].date);
            }
        }
    } catch (e) {
        console.error('Week stats error:', e);
    }
}

function getLocalDateString(date) {
    const year = date.getFullYear();
    const month = String(date.getMonth() + 1).padStart(2, '0');
    const day = String(date.getDate()).padStart(2, '0');
    return `${year}-${month}-${day}`;
}

function parseLocalDateString(dateStr) {
    const [year, month, day] = dateStr.split('-').map(Number);
    return new Date(year, month - 1, day);
}

async function loadSelectedDayMeals(day) {
    const dayStr = getLocalDateString(day);
    document.getElementById('selected-day-title').textContent = `Selected Day: ${dayStr}`;
    try {
        const res = await fetch(`${API_BASE}/api/meals/day/${dayStr}`);
        const data = await res.json();
        const container = document.getElementById('selected-day-meals');

        // Update the weekly macro summary when a day is selected.
        if (currentView === 'weekly') {
            updateMacroSummary(data.total);
        }

        if (!data.meals.length) {
            container.innerHTML = '<p class="text-muted">No meals for this day.</p>';
            return;
        }

        container.innerHTML = `
                    <p class="small">Total: Cal: ${formatCalories(data.total.calories)} | P: ${formatMacro(data.total.protein)}g | F: ${formatMacro(data.total.fat)}g | C: ${formatMacro(data.total.carbs)}g</p>
                    ${data.meals.map(m => `
                        <div class="meal-item">
                            <div class="d-flex justify-content-between">
                                <h6>${m.name}</h6>
                                <button
                                    class="btn btn-sm btn-outline-danger"
                                    onclick="deleteMeal(${m.id}, '${dayStr}')"
                                >
                                    ×
                                </button>
                            </div>
                            <p class="text-muted small mb-0">${m.food_name} - ${m.quantity}g</p>
                        </div>
                    `).join('')}
                `;
    } catch (e) {
        document.getElementById('selected-day-meals').innerHTML = '<p class="text-muted">Error loading.</p>';
    }
}

async function loadSelectedDailyMeals(day) {
    await loadSelectedDayMeals(day);

    // Highlight the selected day button in the week view.
    const dayStr = getLocalDateString(day);
    const buttons = document.querySelectorAll('#week-day-buttons button');
    buttons.forEach(btn => {
        if (btn.dataset.date === dayStr) {
            btn.classList.remove('btn-outline-secondary');
            btn.classList.add('btn-primary');
        } else {
            btn.classList.remove('btn-primary');
            btn.classList.add('btn-outline-secondary');
        }
    });
}

async function selectDayByDateString(dateStr) {
    // Highlight the selected day button first.
    const buttons = document.querySelectorAll('#week-day-buttons button');
    buttons.forEach(btn => {
        if (btn.dataset.date === dateStr) {
            btn.classList.remove('btn-outline-secondary');
            btn.classList.add('btn-primary');
        } else {
            btn.classList.remove('btn-primary');
            btn.classList.add('btn-outline-secondary');
        }
    });

    await loadSelectedDayMeals(parseLocalDateString(dateStr));
}

function switchView(view) {
    currentView = view;
    document.getElementById('daily-view').style.display = view === 'daily' ? 'block' : 'none';
    document.getElementById('weekly-view').style.display = view === 'weekly' ? 'block' : 'none';
    document.getElementById('btn-daily').className = view === 'daily' ? 'btn btn-sm btn-primary' : 'btn btn-sm btn-outline-primary';
    document.getElementById('btn-weekly').className = view === 'weekly' ? 'btn btn-sm btn-primary' : 'btn btn-sm btn-outline-primary';

    if (view === 'daily') loadDayMeals(new Date());
    else {
        const today = new Date();
        const weekStart = new Date(today);
        weekStart.setDate(today.getDate() - today.getDay() + 1);
        loadWeekStats(weekStart);
    }
}

function switchChartMode(mode) {
    if (currentChartMode === mode) return;
    currentChartMode = mode;
    updateChartModeButtons();

    if (currentView === 'weekly') {
        const today = new Date();
        const weekStart = new Date(today);
        weekStart.setDate(today.getDate() - today.getDay() + 1);
        loadWeekStats(weekStart);
    }
}

function updateChartModeButtons() {
    const caloriesBtn = document.getElementById('btn-calories');
    const macrosBtn = document.getElementById('btn-macronutrients');

    if (currentChartMode === 'calories') {
        caloriesBtn.className = 'btn btn-sm btn-primary';
        macrosBtn.className = 'btn btn-sm btn-outline-primary';
    } else {
        caloriesBtn.className = 'btn btn-sm btn-outline-primary';
        macrosBtn.className = 'btn btn-sm btn-primary';
    }
}

function selectNutritionGoal(buttonId) {
    // Reset all buttons to outline-secondary
    const goalButtons = ['goal-cut', 'goal-maintain', 'goal-bulk'];
    goalButtons.forEach(id => {
        document.getElementById(id).className = 'btn btn-outline-secondary';
    });

    // Set the selected button to primary
    document.getElementById(buttonId).className = 'btn btn-primary';

    // Store the selected goal and update guidance text
    const guidanceBox = document.getElementById('target-goal-guidance');
    if (buttonId === 'goal-cut') {
        selectedNutritionGoal = 'cut';
        guidanceBox.textContent = 'Placeholder guidance for cutting. Focus on creating a calorie deficit while maintaining adequate protein intake for muscle preservation.';
    } else if (buttonId === 'goal-maintain') {
        selectedNutritionGoal = 'maintain';
        guidanceBox.textContent = 'Placeholder guidance for maintenance. Consume calories that match your daily energy expenditure to maintain current weight.';
    } else if (buttonId === 'goal-bulk') {
        selectedNutritionGoal = 'bulk';
        guidanceBox.textContent = 'Placeholder guidance for bulking. Focus on a calorie surplus with adequate protein to support muscle growth and recovery.';
    }

    // Calculate and populate macro targets
    calculateMacroTargets();
}

function calculateMacroTargets() {
    const weight = parseFloat(document.getElementById('target-weight').value);
    if (!weight || !selectedNutritionGoal) return;

    let baseCalories;
    if (selectedNutritionGoal === 'cut') {
        baseCalories = weight * 25; // 25 kcal per kg for cutting
    } else if (selectedNutritionGoal === 'maintain') {
        baseCalories = weight * 30; // 30 kcal per kg for maintenance
    } else if (selectedNutritionGoal === 'bulk') {
        baseCalories = weight * 35; // 35 kcal per kg for bulking
    }

    const protein = weight * 1.6; // 1.6g protein per kg body weight
    const fat = weight * 1.0; // 1.0g fat per kg body weight
    const proteinCalories = protein * 4;
    const fatCalories = fat * 9;
    const carbCalories = baseCalories - proteinCalories - fatCalories;
    const carbs = carbCalories / 4;

    // Populate the form inputs
    document.getElementById('target-calories').value = Math.round(baseCalories);
    document.getElementById('target-protein').value = protein.toFixed(1);
    document.getElementById('target-fat').value = fat.toFixed(1);
    document.getElementById('target-carbs').value = Math.max(0, carbs.toFixed(1));
}

async function addMeal(e) {
    e.preventDefault();
    const selectedFoodId = parseInt(document.getElementById('meal-food').value);
    const selectedFood = foods.find(f => f.id === selectedFoodId);
    const meal = {
        date: document.getElementById('meal-date').value,
        name: selectedFood ? selectedFood.name : 'Meal',
        food_id: selectedFoodId,
        quantity: parseFloat(document.getElementById('meal-quantity').value)
    };

    await fetch(`${API_BASE}/api/meals/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(meal)
    });

    bootstrap.Modal.getInstance(document.getElementById('addMealModal')).hide();
    document.getElementById('add-meal-form').reset();
    document.getElementById('meal-date').value = new Date().toISOString().split('T')[0];

    if (currentView === 'daily') await loadDayMeals(new Date());
    else {
        const today = new Date();
        const weekStart = new Date(today);
        weekStart.setDate(today.getDate() - today.getDay() + 1);
        await loadWeekStats(weekStart);
    }
}

async function saveCustomMeal(e) {
    e.preventDefault();

    const name = document.getElementById('custom-meal-name').value.trim();
    const protein = parseFloat(document.getElementById('custom-meal-protein').value) || 0;
    const fat = parseFloat(document.getElementById('custom-meal-fat').value) || 0;
    const carbs = parseFloat(document.getElementById('custom-meal-carbs').value) || 0;
    const calories = protein * 4 + fat * 9 + carbs * 4;

    const newFood = {
        name,
        calories_per_100g: calories,
        protein_per_100g: protein,
        fat_per_100g: fat,
        carbs_per_100g: carbs
    };

    try {
        const res = await fetch(`${API_BASE}/api/foods/`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(newFood)
        });

        if (!res.ok) {
            const error = await res.json();
            alert(error.detail);
            return;
        }

        const createdFood = await res.json();
        console.log('Created custom food:', createdFood);

        await refreshFoodOptions(createdFood.id);
        document.getElementById('custom-meal-form').reset();
        document.getElementById('standard-meal-fields').style.display = '';
        document.getElementById('custom-meal-fields').style.display = 'none';
    } catch (error) {
        console.error('Custom food creation failed:', error);
    }
}

async function updateTarget(e) {
    e.preventDefault();
    const target = {
        calories: parseInt(document.getElementById('target-calories').value),
        protein: parseFloat(document.getElementById('target-protein').value),
        fat: parseFloat(document.getElementById('target-fat').value),
        carbs: parseFloat(document.getElementById('target-carbs').value)
    };

    await fetch(`${API_BASE}/api/target`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(target)
    });

    bootstrap.Modal.getInstance(document.getElementById('editTargetModal')).hide();
    await loadTarget();
    if (currentView === 'daily') await loadDayMeals(new Date());
}

async function loadRecipes() {
    try {
        const res = await fetch(`${API_BASE}/api/recipes`);
        const recipes = await res.json();
        document.getElementById('recipes-list').innerHTML = recipes.map(r => `
                    <div class="mb-4">
                        <h5>${r.name}</h5>
                        <p class="text-muted">${r.description}</p>
                        <pre style="white-space: pre-wrap; background: #f8f9fa; padding: 10px; border-radius: 5px;">${r.instructions}</pre>
                    </div>
                `).join('');
        new bootstrap.Modal(document.getElementById('recipesModal')).show();
    } catch (e) {
        alert('Recipes could not be loaded.');
    }
}
