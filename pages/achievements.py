import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
from auth import require_auth
from models import get_user_achievements, get_user_stats, get_leaderboard
from utils import format_datetime

@require_auth
def show():
    """Display achievements and gamification dashboard"""
    st.title("🏆 Achievements & Performance")
    
    current_user = st.session_state.get("username", "Unknown")
    
    # User stats overview
    user_stats = get_user_stats(current_user)
    
    # Achievement overview cards
    st.subheader("📊 Your Performance Overview")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "Cases Handled", 
            user_stats.get("total_cases", 0),
            delta=f"+{user_stats.get('cases_this_month', 0)} this month"
        )
    
    with col2:
        avg_resolution = user_stats.get("avg_resolution_time", 0)
        st.metric(
            "Avg Resolution", 
            f"{avg_resolution:.1f} days",
            delta=f"{-0.5 if avg_resolution < 3 else 0.3} vs target"
        )
    
    with col3:
        quality_score = user_stats.get("quality_score", 0)
        st.metric(
            "Quality Score", 
            f"{quality_score:.1f}/100",
            delta=f"+{user_stats.get('quality_improvement', 0):.1f}"
        )
    
    with col4:
        st.metric(
            "Achievement Points", 
            user_stats.get("total_points", 0),
            delta=f"+{user_stats.get('points_this_week', 0)} this week"
        )
    
    st.divider()
    
    # Achievement badges
    st.subheader("🎖️ Your Achievements")
    
    achievements = get_user_achievements(current_user)
    
    if achievements:
        # Group achievements by category
        categories = {}
        for achievement in achievements:
            category = achievement.get("category", "General")
            if category not in categories:
                categories[category] = []
            categories[category].append(achievement)
        
        # Display achievements by category
        for category, category_achievements in categories.items():
            st.write(f"**{category}**")
            
            # Create columns for badges
            cols = st.columns(min(len(category_achievements), 4))
            
            for i, achievement in enumerate(category_achievements):
                with cols[i % 4]:
                    # Achievement badge
                    badge_color = get_badge_color(achievement["tier"])
                    st.markdown(f"""
                    <div style='text-align: center; padding: 15px; border: 2px solid {badge_color}; border-radius: 10px; margin: 5px;'>
                        <div style='font-size: 2em;'>{achievement['icon']}</div>
                        <div style='font-weight: bold; color: {badge_color};'>{achievement['name']}</div>
                        <div style='font-size: 0.8em; color: gray;'>{achievement['description']}</div>
                        <div style='font-size: 0.7em; margin-top: 5px;'>Earned: {format_datetime(achievement['earned_at'])}</div>
                    </div>
                    """, unsafe_allow_html=True)
            
            if len(category_achievements) % 4 != 0:
                # Fill remaining columns
                for j in range(len(category_achievements) % 4, 4):
                    with cols[j]:
                        st.empty()
    else:
        st.info("🎯 Start handling cases to earn your first achievements!")
    
    st.divider()
    
    # Progress tracking
    st.subheader("📈 Progress Tracking")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Case resolution trend
        resolution_data = user_stats.get("resolution_trend", [])
        if resolution_data:
            fig = px.line(
                x=[item["date"] for item in resolution_data],
                y=[item["cases"] for item in resolution_data],
                title="Cases Resolved Over Time",
                labels={"x": "Date", "y": "Cases Resolved"}
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No case resolution data available yet")
    
    with col2:
        # Quality score progress
        quality_data = user_stats.get("quality_trend", [])
        if quality_data:
            fig = px.line(
                x=[item["date"] for item in quality_data],
                y=[item["score"] for item in quality_data],
                title="Quality Score Trend",
                labels={"x": "Date", "y": "Quality Score"}
            )
            fig.add_hline(y=80, line_dash="dash", line_color="green", annotation_text="Target: 80")
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No quality score data available yet")
    
    st.divider()
    
    # Leaderboard
    st.subheader("🏅 Leaderboard")
    
    leaderboard_type = st.selectbox(
        "Leaderboard Type",
        ["Overall Points", "Cases This Month", "Quality Score", "Speed Champions"]
    )
    
    leaderboard_data = get_leaderboard(leaderboard_type.lower().replace(" ", "_"))
    
    if leaderboard_data:
        # Create leaderboard display
        leaderboard_df = []
        for i, user in enumerate(leaderboard_data, 1):
            rank_icon = get_rank_icon(i)
            leaderboard_df.append({
                "Rank": f"{rank_icon} {i}",
                "User": user["name"] or user["username"],
                "Score": user["score"],
                "Team": user.get("team", "N/A")
            })
        
        st.dataframe(leaderboard_df, use_container_width=True, hide_index=True)
        
        # Highlight current user's position
        user_rank = next((i for i, user in enumerate(leaderboard_data, 1) 
                         if user["username"] == current_user), None)
        if user_rank:
            if user_rank <= 3:
                st.success(f"🎉 Congratulations! You're ranked #{user_rank}")
            elif user_rank <= 10:
                st.info(f"👍 Great job! You're in the top 10 (#{user_rank})")
            else:
                st.write(f"📊 Your current rank: #{user_rank}")
    else:
        st.info("Leaderboard data will appear as users handle more cases")
    
    st.divider()
    
    # Available achievements to unlock
    st.subheader("🎯 Achievements to Unlock")
    
    available_achievements = get_available_achievements(current_user)
    
    if available_achievements:
        for achievement in available_achievements[:6]:  # Show top 6 unlockable
            progress = achievement.get("progress", 0)
            target = achievement.get("target", 100)
            
            st.markdown(f"**{achievement['icon']} {achievement['name']}**")
            st.write(achievement['description'])
            
            # Progress bar
            progress_bar = st.progress(progress / target)
            st.write(f"Progress: {progress}/{target} ({progress/target*100:.1f}%)")
            
            if progress >= target * 0.8:  # 80% complete
                st.info("🔥 Almost there! Keep up the great work!")
            
            st.write("---")
    else:
        st.info("🌟 All available achievements unlocked! More coming soon...")

def get_badge_color(tier):
    """Get color for achievement badge based on tier"""
    colors = {
        "bronze": "#CD7F32",
        "silver": "#C0C0C0", 
        "gold": "#FFD700",
        "platinum": "#E5E4E2",
        "diamond": "#B9F2FF"
    }
    return colors.get(tier.lower(), "#808080")

def get_rank_icon(rank):
    """Get icon for leaderboard rank"""
    if rank == 1:
        return "🥇"
    elif rank == 2:
        return "🥈"
    elif rank == 3:
        return "🥉"
    elif rank <= 10:
        return "🏆"
    else:
        return "📊"

def get_available_achievements(username):
    """Get achievements that user can still unlock"""
    # This would be implemented with actual achievement logic
    return [
        {
            "name": "Speed Demon",
            "description": "Resolve 10 cases in under 2 days each",
            "icon": "⚡",
            "progress": 7,
            "target": 10,
            "tier": "silver"
        },
        {
            "name": "Quality Master",
            "description": "Maintain 95+ quality score for 30 days",
            "icon": "💎",
            "progress": 25,
            "target": 30,
            "tier": "gold"
        },
        {
            "name": "Case Crusher",
            "description": "Handle 100 cases successfully",
            "icon": "💪",
            "progress": 85,
            "target": 100,
            "tier": "bronze"
        }
    ]