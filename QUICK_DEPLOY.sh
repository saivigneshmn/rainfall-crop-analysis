#!/bin/bash
# Quick deployment script for local ngrok tunnel

echo "🚀 Starting Streamlit app on port 8501..."
streamlit run streamlit_app.py &
STREAMLIT_PID=$!

echo "⏳ Waiting for Streamlit to start..."
sleep 5

echo "🌐 Starting ngrok tunnel..."
ngrok http 8501 &
NGROK_PID=$!

echo ""
echo "✅ Deployment started!"
echo "📋 Streamlit PID: $STREAMLIT_PID"
echo "📋 Ngrok PID: $NGROK_PID"
echo ""
echo "🔗 Your public URL will appear in ngrok output above"
echo "💡 Press Ctrl+C to stop both services"
echo ""

# Wait for interrupt
wait

