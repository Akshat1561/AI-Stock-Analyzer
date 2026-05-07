document.addEventListener("DOMContentLoaded", function () {
  let stockChart = null;
  const tickerInput = document.getElementById("tickerInput");
  const suggestionsBox = document.getElementById("suggestionsBox");
  const loadingDiv = document.getElementById("loading");

  const popularStocks = [
    // === US STOCKS ===
    { symbol: "AAPL", name: "Apple Inc." },
    { symbol: "MSFT", name: "Microsoft Corp." },
    { symbol: "GOOGL", name: "Alphabet (Google)" },
    { symbol: "AMZN", name: "Amazon.com Inc." },
    { symbol: "TSLA", name: "Tesla Inc." },
    { symbol: "NVDA", name: "NVIDIA Corp." },
    { symbol: "META", name: "Meta Platforms" },
    { symbol: "NFLX", name: "Netflix Inc." },
    { symbol: "AMD", name: "Advanced Micro Devices" },
    { symbol: "INTC", name: "Intel Corporation" },
    { symbol: "JPM", name: "JPMorgan Chase" },
    { symbol: "V", name: "Visa Inc." },
    { symbol: "WMT", name: "Walmart Inc." },
    { symbol: "KO", name: "Coca-Cola" },
    { symbol: "DIS", name: "Walt Disney" },
    { symbol: "PEP", name: "PepsiCo Inc." },
    { symbol: "COST", name: "Costco Wholesale" },
    { symbol: "MCD", name: "McDonald’s Corp." },
    { symbol: "NKE", name: "Nike Inc." },
    { symbol: "CRM", name: "Salesforce Inc." },
    { symbol: "UBER", name: "Uber Technologies" },
    { symbol: "PYPL", name: "PayPal Holdings" },
    { symbol: "BA", name: "Boeing Co." },
    { symbol: "IBM", name: "IBM Corporation" },
    { symbol: "SBUX", name: "Starbucks Corp." },

    // === INDIAN STOCKS ===
    { symbol: "RELIANCE.NS", name: "Reliance Industries" },
    { symbol: "TCS.NS", name: "Tata Consultancy Services" },
    { symbol: "HDFCBANK.NS", name: "HDFC Bank" },
    { symbol: "ICICIBANK.NS", name: "ICICI Bank" },
    { symbol: "INFY.NS", name: "Infosys Limited" },
    { symbol: "SBIN.NS", name: "State Bank of India" },
    { symbol: "TATAMOTORS.NS", name: "Tata Motors" },
    { symbol: "ITC.NS", name: "ITC Limited" },
    { symbol: "WIPRO.NS", name: "Wipro Limited" },
    { symbol: "LT.NS", name: "Larsen & Toubro" },
    { symbol: "TATASTEEL.NS", name: "Tata Steel" },
    { symbol: "SUNPHARMA.NS", name: "Sun Pharma" },
    { symbol: "BAJFINANCE.NS", name: "Bajaj Finance" },
    { symbol: "MARUTI.NS", name: "Maruti Suzuki" },
    { symbol: "ZOMATO.NS", name: "Zomato Limited" },
    { symbol: "HINDUNILVR.NS", name: "Hindustan Unilever" },
    { symbol: "KOTAKBANK.NS", name: "Kotak Mahindra Bank" },
    { symbol: "AXISBANK.NS", name: "Axis Bank" },
    { symbol: "ASIANPAINT.NS", name: "Asian Paints" },
    { symbol: "M&M.NS", name: "Mahindra & Mahindra" },
    { symbol: "TITAN.NS", name: "Titan Company" },
    { symbol: "NTPC.NS", name: "NTPC Limited" },
    { symbol: "ULTRACEMCO.NS", name: "UltraTech Cement" },
    { symbol: "POWERGRID.NS", name: "Power Grid Corporation" },
    { symbol: "BHEL.NS", name: "Bharat Heavy Electricals" },
  ];

  // === AUTOCOMPLETE CODE ===
  if (tickerInput && suggestionsBox) {
    tickerInput.addEventListener("input", function () {
      const query = this.value.toLowerCase().trim();
      suggestionsBox.innerHTML = "";

      if (!query) {
        suggestionsBox.style.display = "none";
        return;
      }

      const matches = popularStocks.filter(
        (stock) =>
          stock.symbol.toLowerCase().includes(query) ||
          stock.name.toLowerCase().includes(query),
      );

      if (matches.length > 0) {
        suggestionsBox.style.display = "block";
        matches.forEach((match) => {
          const div = document.createElement("div");
          div.className = "suggestion-item";
          div.innerHTML = `<span class="sugg-sym">${match.symbol}</span> <span class="sugg-name">${match.name}</span>`;

          div.onclick = function () {
            tickerInput.value = match.symbol;
            suggestionsBox.style.display = "none";
          };
          suggestionsBox.appendChild(div);
        });
      } else {
        suggestionsBox.style.display = "none";
      }
    });

    document.addEventListener("click", function (e) {
      if (e.target !== tickerInput && e.target !== suggestionsBox) {
        suggestionsBox.style.display = "none";
      }
    });
  }

  // === VIBRANT "MOUNTAIN STYLE" CHART RENDERER ===
  function drawColorfulChart(data) {
    const canvas = document.getElementById("myFinancialChart");
    const ctx = canvas.getContext("2d");
    if (stockChart) {
      stockChart.destroy();
    }

    const chartAreaHeight = canvas.height || 400;

    //  1. Mountain Fill Gradient (Teal to Transparent)
    const mountainGradient = ctx.createLinearGradient(0, 0, 0, chartAreaHeight);
    mountainGradient.addColorStop(0, "rgba(0, 229, 192, 0.4)");
    mountainGradient.addColorStop(1, "rgba(0, 229, 192, 0)");

    //  AI Prediction Line Gradient
    const aiLineGradient = ctx.createLinearGradient(
      0,
      0,
      canvas.width || 800,
      0,
    );
    aiLineGradient.addColorStop(0, "#ff9f43");
    aiLineGradient.addColorStop(1, "#ff4757");

    // Last close price
    const lastActualPrice = data.history_close[data.history_close.length - 1];

    //  2. Custom Plugin: Red Dashed Current Price Line
    const currentPriceLinePlugin = {
      id: "currentPriceLine",
      beforeDraw: (chart) => {
        const {
          ctx,
          chartArea: { left, right },
          scales: { y },
        } = chart;
        const yPos = y.getPixelForValue(lastActualPrice);

        ctx.save();
        ctx.beginPath();
        ctx.moveTo(left, yPos);
        ctx.lineTo(right, yPos);
        ctx.lineWidth = 1;
        ctx.strokeStyle = "#ff4757";
        ctx.setLineDash([4, 4]);
        ctx.stroke();
        ctx.restore();
      },
    };

    stockChart = new Chart(ctx, {
      type: "line",
      data: {
        labels: data.labels,
        datasets: [
          {
            label: "Actual Price (Mountain)",
            data: data.history_close,
            borderColor: "#00e5c0",
            backgroundColor: mountainGradient,
            borderWidth: 2,
            pointRadius: 0,
            tension: 0.1,
            fill: true,
          },
          {
            label: "Moving Average (SMA 20)",
            data: data.sma_20,
            borderColor: "rgba(255, 255, 255, 0.2)",
            borderWidth: 1.5,
            borderDash: [5, 5],
            pointRadius: 0,
            tension: 0.4,
          },
          {
            label: "AI Trend Prediction",
            data: data.pred_line,
            borderColor: aiLineGradient,
            borderWidth: 3,
            pointRadius: 0,
            tension: 0.4,
            shadowColor: "rgba(255, 71, 87, 0.5)",
            shadowBlur: 10,
          },
        ],
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        interaction: { mode: "index", intersect: false },
        plugins: {
          legend: {
            labels: {
              color: "#ffffff",
              font: { family: "Poppins" },
              usePointStyle: true,
            },
          },
          tooltip: {
            backgroundColor: "#111827",
            titleColor: "#00e5c0",
            borderColor: "rgba(255,255,255,0.1)",
            borderWidth: 1,
          },
        },
        scales: {
          x: {
            type: "time",

            time: {
              unit: "day",

              tooltipFormat: "yyyy-MM-dd",

              displayFormats: {
                day: "MM-dd",
              },
            },

            ticks: {
              color: "#888",
            },

            grid: {
              display: false,
            },
          },
          y: {
            position: "right",

            grace: "5%",

            ticks: {
              color: "#888",

              padding: 10,

              callback: function (value) {
                return data.currency_symbol + value.toFixed(0);
              },
            },

            grid: {
              color: "rgba(255,255,255,0.05)",
              drawBorder: false,
            },
          },
        },
      },
      plugins: [currentPriceLinePlugin],
    });
  }

  // === MAIN ANALYZE FUNCTION ===
  window.analyzeStock = async function () {
    let ticker = tickerInput.value.trim();
    let timeframe = document.getElementById("timeframeSelect").value;

    let foundStock = popularStocks.find(
      (s) => s.name.toLowerCase() === ticker.toLowerCase(),
    );
    if (foundStock) ticker = foundStock.symbol;

    if (!ticker) {
      alert("Please enter a stock ticker!");
      return;
    }

    loadingDiv.style.display = "block";

    try {
      const response = await fetch(
        `/predict_real_stock?ticker=${encodeURIComponent(ticker)}&timeframe=${timeframe}`,
      );
      const data = await response.json();

      if (data.error) {
        alert("Error: " + data.error);
        loadingDiv.style.display = "none";
        return;
      }

      // Update DOM Data
      document.getElementById("rmse").innerText = data.rmse;
      document.getElementById("r2").innerText = data.r2;
      document.getElementById("lastPrice").innerText =
        data.currency_symbol + data.current_price;
      document.getElementById("predictedPrice").innerText =
        data.currency_symbol + data.predicted_price;
      document.getElementById("rsiValue").innerText = data.latest_rsi;
      document.getElementById("stochValue").innerText = data.latest_stoch;
      document.getElementById("vwapValue").innerText =
        data.currency_symbol + data.latest_vwap;

      // Draw Graph
      drawColorfulChart(data);
    } catch (error) {
      console.error("Fetch error:", error);
      alert("Failed to connect to backend server.");
    }

    loadingDiv.style.display = "none";
  };
});

const stochElement = document.getElementById("stochValue");
if (stochElement) {
  stochElement.innerText = data.latest_stoch;
}
