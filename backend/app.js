// Aca
        const API_BASE = window.location.protocol === 'file:'
            ? 'http://localhost:8000'
            : window.location.origin;
        let currentView = 'daily';
        let currentTarget = null;
        let foods = [];
        let weekChart = null;

        document.addEventListener('DOMContentLoaded', async () => {
            // Load Food List
            try {
                const res = await fetch(`${API_BASE}/api/foods/`);
                if (!res.ok) {
                    console.error('Failed to fetch foods:', res.status, res.statusText);
                    throw new Error(`HTTP error! status: ${res.status}`);
                }
                foods = await res.json();
                console.log('Foods loaded:', foods);
                const foodSelect = document.getElementById('meal-food');
                if (foods.length === 0) {
                    const opt = document.createElement('option');
                    opt.value = '';
                    opt.textContent = 'No foods available';
                    opt.disabled = true;
                    foodSelect.appendChild(opt);
                } else {
                    foods.forEach(f => {
                        const opt = document.createElement('option');
                        opt.value = f.id;
                        opt.textContent = f.name;
                        foodSelect.appendChild(opt);
                    });
                }
            } catch(e) { 
                console.error("Cannot load foods:", e); 
                const foodSelect = document.getElementById('meal-food');
                const opt = document.createElement('option');
                opt.value = '';
                opt.textContent = 'Error loading foods';
                opt.disabled = true;
                foodSelect.appendChild(opt);
            }

            // The default date is today
            document.getElementById('meal-date').value = new Date().toISOString().split('T')[0];

            // Load Target
            await loadTarget();

            // Load today's meal times
            await loadDayMeals(new Date());

            // Event Binding
            document.getElementById('btn-daily').addEventListener('click', () => switchView('daily'));
            document.getElementById('btn-weekly').addEventListener('click', () => switchView('weekly'));
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
            document.getElementById('edit-target-form').addEventListener('submit', updateTarget);
        });

        async function loadTarget() {
            try {
                const res = await fetch(`${API_BASE}/api/target`);
                currentTarget = await res.json();
            } catch(e) {
                currentTarget = { calories: 2000, protein: 50, fat: 65, carbs: 250 };
            }
            updateMacroSummary();
        }

        function updateMacroSummary(totals = null) {
            if (!totals) totals = { calories: 0, protein: 0, fat: 0, carbs: 0 };
            document.getElementById('macro-summary').innerHTML = `
                <div class="macro-item"><span>Calories</span><span><strong>${totals.calories || 0}</strong> / ${currentTarget.calories}</span></div>
                <div class="macro-item"><span>Protein</span><span><strong>${totals.protein || 0}</strong>g / ${currentTarget.protein}g</span></div>
                <div class="macro-item"><span>Fat</span><span><strong>${totals.fat || 0}</strong>g / ${currentTarget.fat}g</span></div>
                <div class="macro-item"><span>Carbs</span><span><strong>${totals.carbs || 0}</strong>g / ${currentTarget.carbs}g</span></div>
            `;
        }

        async function loadDayMeals(day) {
            const dayStr = day.toISOString().split('T')[0];
            try {
                const res = await fetch(`${API_BASE}/api/meals/day/${dayStr}`);
                if (!res.ok) throw new Error("No data");
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
                    div class="meal-item">
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
        Cal: ${m.calories}
        | P: ${m.protein}g
        | F: ${m.fat}g
        | C: ${m.carbs}g
    </small>
</div>
                `).join('');
            } catch(e) {
                document.getElementById('meals-list').innerHTML = '<p class="text-muted">Could not load meals.</p>';
            }
        }

        async function deleteMeal(mealId) {
            await fetch(`${API_BASE}/api/meals/${mealId}`, { method: 'DELETE' });
            await loadDayMeals(new Date());
        }

        async function loadWeekStats(weekStart) {
            const startStr = weekStart.toISOString().split('T')[0];
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

                if (weekChart) weekChart.destroy();
                const ctx = document.getElementById('week-chart').getContext('2d');
                weekChart = new Chart(ctx, {
                    type: 'line',
                    data: {
                        labels,
                        datasets: [
                            { label: 'Calories', data: calories, borderColor: '#0d6efd', tension: 0.1 },
                            { label: 'Protein (g)', data: protein, borderColor: '#198754', tension: 0.1 },
                            { label: 'Fat (g)', data: fat, borderColor: '#ffc107', tension: 0.1 },
                            { label: 'Carbs (g)', data: carbs, borderColor: '#dc3545', tension: 0.1 }
                        ]
                    },
                    options: {
                        responsive: true,
                        onClick: async(e) => {
                            
                            const points = weekChart.getElementsAtEventForMode(e, 'nearest', { intersect: false }, true);

                            if (points.length) {
                                const index = points[0].index;
                                const dayDate = data.daily_stats[index].date;
                                await selectDayByDateString(dayDate);
                        }

                    }
                }                });

                // Render clickable day buttons
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

                // Select today by default
                const today = new Date().toISOString().split('T')[0];
                const todayStats = data.daily_stats.find(d => d.date === today);
                if (todayStats) {
                    await selectDayByDateString(todayStats.date);
                } else {
                    // If today is not in the week stats, select the first day
                    await selectDayByDateString(data.daily_stats[0].date);
                }
            } catch(e) {
                console.error("Week stats error:", e);
            }
        }

        async function loadSelectedDayMeals(day) {
            const dayStr = day.toISOString().split('T')[0];
            document.getElementById('selected-day-title').textContent = `Selected Day: ${dayStr}`;
            try {
                const res = await fetch(`${API_BASE}/api/meals/day/${dayStr}`);
                const data = await res.json();
                const container = document.getElementById('selected-day-meals');
                
                // Update macro summary for the weekly view
                if (currentView === 'weekly') {
                    updateMacroSummary(data.total);
                }
                
                if (!data.meals.length) {
                    container.innerHTML = '<p class="text-muted">No meals for this day.</p>';
                    return;
                }
                container.innerHTML = `
                    <p class="small">Total: Cal: ${data.total.calories} | P: ${data.total.protein}g | F: ${data.total.fat}g | C: ${data.total.carbs}g</p>
                    ${data.meals.map(m => `
                        <div class="meal-item">
                            <h6>${m.name}</h6>
                            <p class="text-muted small mb-0">${m.food_name} - ${m.quantity}g</p>
                        </div>
                    `).join('')}
                `;
            } catch(e) {
                document.getElementById('selected-day-meals').innerHTML = '<p class="text-muted">Error loading.</p>';
            }
        }

        async function loadSelectedDailyMeals(day) {
            await loadSelectedDayMeals(day);
            
            // Highlight the selected day button
            const dayStr = day.toISOString().split('T')[0];
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
            // Highlight the button immediately
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
            
            // Load the meals for that day
            await loadSelectedDayMeals(new Date(dateStr + 'T00:00:00'));
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

        async function addMeal(e) {
            e.preventDefault();
            const meal = {
                date: document.getElementById('meal-date').value,
                name: document.getElementById('meal-name').value,
                food_id: parseInt(document.getElementById('meal-food').value),
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
            } catch(e) { alert("Recipes could not be loaded."); }
        }
