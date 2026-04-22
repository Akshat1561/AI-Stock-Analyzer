let myStockChart = null;

// 📚 Built-in Database of Popular Stocks (US & India)
const popularStocks = [
    { symbol: 'AAPL', name: 'Apple Inc.' },
    { symbol: 'MSFT', name: 'Microsoft Corp.' },
    { symbol: 'GOOGL', name: 'Alphabet (Google)' },
    { symbol: 'AMZN', name: 'Amazon.com Inc.' },
    { symbol: 'TSLA', name: 'Tesla Inc.' },
    { symbol: 'NVDA', name: 'NVIDIA Corp.' },
    { symbol: 'META', name: 'Meta Platforms' },
    { symbol: 'RELIANCE.NS', name: 'Reliance Industries' },
    { symbol: 'TCS.NS', name: 'Tata Consultancy' },
    { symbol: 'HDFCBANK.NS', name: 'HDFC Bank' },
    { symbol: 'INFY.NS', name: 'Infosys Limited' },
    { symbol: 'SBIN.NS', name: 'State Bank of India' },
    { symbol: 'TATAMOTORS.NS', name: 'Tata Motors' },
    { symbol: 'ITC.NS', name: 'ITC Limited' },
    { symbol: 'ICICIBANK.NS', name: 'ICICI Bank' },
    { symbol: 'WMT', name: 'Walmart Inc.' },
    { symbol: 'JPM', name: 'JPMorgan Chase' }
];

function goToDashboard() {
    const tickerInput = document.getElementById('tickerInput');
    const timeframeSelect = document.getElementById('timeframeSelect');

    if (tickerInput && timeframeSelect) {
        const ticker = tickerInput.value.trim();
        const timeframe = timeframeSelect.value;
        if (ticker) {
            window.location.href = `dashboard.html?ticker=${ticker}&timeframe=${timeframe}`;
        } else {
            alert("Please enter a stock ticker.");
        }
    }
}

document.addEventListener('DOMContentLoaded', () => {
    
    // ==========================================
    // 🔍 AUTOCOMPLETE LOGIC (Landing Page)
    // ==========================================
    const tickerInput = document.getElementById('tickerInput');
    const suggestionsList = document.getElementById('suggestionsList');

    if (tickerInput && suggestionsList) {
        // Listen to every keystroke
        tickerInput.addEventListener('input', function() {
            const query = this.value.toLowerCase().trim();
            suggestionsList.innerHTML = ''; // Clear previous suggestions
            
            if (query === '') {
                suggestionsList.style.display = 'none';
                return;
            }

            // Find matching stocks by Symbol OR Company Name
            const filtered = popularStocks.filter(stock => 
                stock.symbol.toLowerCase().includes(query) || 
                stock.name.toLowerCase().includes(query)
            );

            // Populate the dropdown
            if (filtered.length > 0) {
                suggestionsList.style.display = 'block';
                filtered.forEach(stock => {
                    const li = document.createElement('li');
                    li.innerHTML = `<span class="ticker-symbol">${stock.symbol}</span> <span class="ticker-name">${stock.name}</span>`;
                    
                    // When user clicks a recommendation, auto-fill the input
                    li.addEventListener('click', () => {
                        tickerInput.value = stock.symbol;
                        suggestionsList.style.display = 'none';
                    });
                    
                    suggestionsList.appendChild(li);
                });
            } else {
                suggestionsList.style.display = 'none';
            }
        });

        // Hide dropdown if user clicks somewhere else on the page
        document.addEventListener('click', function(e) {
            if (e.target !== tickerInput && e.target !== suggestionsList) {
                suggestionsList.style.display = 'none';
            }
        });
    }

    // ==========================================
    // 📈 DASHBOARD LOGIC (Dashboard Page)
    // ==========================================
    const stockChartCanvas = document.getElementById('stockChart');
    if (stockChartCanvas) {
        const urlParams = new URLSearchParams(window.location.search);
        const ticker = urlParams.get('ticker') || 'AAPL';
        const timeframe = urlParams.get('timeframe') || '1d';
        
        document.getElementById('stockTitle').innerText = `Analysis for: ${ticker.toUpperCase()} (${timeframe})`;
        const boxTitle = timeframe === '1m' ? 'Predicted Next Minute' : 
                         timeframe === '1h' ? 'Predicted Next Hour' : 'Predicted Next Day';
        document.getElementById('predictionTitle').innerText = boxTitle;

        fetchModelData(ticker, timeframe);
    }
});

// ... (KEEP your existing fetchModelData function below this exactly as it is) ...
async function fetchModelData(ticker, timeframe) {
    try {
        const response = await fetch(`https://ai-stock-analyzer-ade6.onrender.com/predict_real_stock?ticker=${ticker}&timeframe=${timeframe}`);        const data = await response.json();

        if (data.error) {
            document.getElementById('loading').innerText = "Error: " + data.error;
            document.getElementById('loading').style.color = "red";
            return;
        }

        document.getElementById('loading').style.display = 'none';
        document.getElementById('dashboard-content').style.display = 'block';

        document.getElementById('rmse').innerText = data.rmse;
        document.getElementById('r2').innerText = data.r2;
        document.getElementById('lastPrice').innerText = data.currency_symbol + data.last_price;
        
        const nextDayElement = document.getElementById('nextDay');
        const diff = data.prediction - data.last_price;
        
        nextDayElement.innerText = data.currency_symbol + data.prediction;
        if (diff > 0) {
            nextDayElement.style.color = "#16a34a"; 
            nextDayElement.innerText += " ▲";
        } else {
            nextDayElement.style.color = "#dc2626"; 
            nextDayElement.innerText += " ▼";
        }

        const graphLabels = data.dates;
        const actualPrices = data.actual;
        const predictedPrices = data.predicted;

        graphLabels.push(data.next_date + " (FUTURE)"); 
        actualPrices.push(null); 
        predictedPrices.push(data.prediction); 

        const ctx = document.getElementById('stockChart').getContext('2d');
        const gradientBlue = ctx.createLinearGradient(0, 0, 0, 400);
        gradientBlue.addColorStop(0, 'rgba(37, 99, 235, 0.5)'); 
        gradientBlue.addColorStop(1, 'rgba(37, 99, 235, 0.0)'); 

        if (myStockChart) myStockChart.destroy();

        myStockChart = new Chart(ctx, {
            type: 'line',
            data: {
                labels: graphLabels,
                datasets: [
                    { 
                        label: 'Actual Price', 
                        data: actualPrices, 
                        borderColor: '#2563eb', 
                        backgroundColor: gradientBlue, 
                        borderWidth: 2.5,
                        pointRadius: 0, 
                        pointHoverRadius: 6, 
                        tension: 0.4, 
                        fill: true 
                    },
                    { 
                        label: 'Predicted Price', 
                        data: predictedPrices, 
                        borderColor: '#dc2626', 
                        borderWidth: 2,
                        borderDash: [5, 5], 
                        pointRadius: 0,
                        pointHoverRadius: 6,
                        tension: 0.4,
                        fill: false 
                    }
                ]
            },
            options: { 
                responsive: true, 
                maintainAspectRatio: false,
                interaction: { mode: 'index', intersect: false },
                plugins: {
                    legend: { position: 'top', labels: { usePointStyle: true, font: { family: "'Inter', sans-serif", size: 13 } } },
                    tooltip: {
                        backgroundColor: 'rgba(15, 23, 42, 0.9)', 
                        titleFont: { size: 13, family: "'Inter', sans-serif" },
                        bodyFont: { size: 14, family: "'Inter', sans-serif", weight: 'bold' },
                        padding: 12, cornerRadius: 8,
                        callbacks: {
                            label: function(context) {
                                if (context.parsed.y === null) return null; 
                                return ` ${context.dataset.label}: ${data.currency_symbol}${context.parsed.y.toFixed(2)}`;
                            }
                        }
                    }
                },
                scales: {
                    x: { grid: { display: false }, ticks: { maxTicksLimit: 8, font: { family: "'Inter', sans-serif" } } },
                    y: {
                        grid: { color: '#f1f5f9', drawBorder: false }, 
                        ticks: { 
                            font: { family: "'Inter', sans-serif" },
                            callback: function(value) { return data.currency_symbol + value; }
                        }
                    }
                }
            }
        });

    } catch (error) {
        document.getElementById('loading').innerText = "Failed to connect to backend.";
        document.getElementById('loading').style.color = "red";
    }
}