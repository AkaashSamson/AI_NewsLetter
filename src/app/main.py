import sys
import os
from pathlib import Path

# Add project root to path so 'src' module can be found
# Resolves: c:\DEV\Project\AI_Engineering\AI_NewsLetter\src\app\main.py -> c:\DEV\Project\AI_Engineering\AI_NewsLetter
root_path = Path(__file__).parent.parent.parent
sys.path.append(str(root_path))

import streamlit as st
from src.database.core import get_db, engine, Base
from src.services.channel_manager import ChannelManager
from src.services.feed_manager import FeedManager
from src.database import crud
from datetime import datetime

# Initialize Tables (For dev simplicity, can be moved to a migration script)
Base.metadata.create_all(bind=engine)


def main():
    st.set_page_config(page_title="AI Newsletter Dashboard", layout="wide")
    st.title("🤖 AI Newsletter Dashboard")

    # Dependency Injection
    db = next(get_db())
    channel_mgr = ChannelManager(db)
    feed_mgr = FeedManager(db)

    # Sidebar: Actions
    with st.sidebar:
        st.header("Manage Channels")

        # Add Channel Form
        with st.form("add_channel"):
            new_url = st.text_input("YouTube Channel URL")
            submitted = st.form_submit_button("Add Channel")
            if submitted and new_url:
                try:
                    with st.spinner("Resolving Channel..."):
                        msg = channel_mgr.add_new_channel(new_url)
                    if "Successfully" in msg:
                        st.success(msg)
                    else:
                        st.warning(msg)
                except Exception as e:
                    st.error(f"Error: {e}")

        st.divider()

        # Manual Trigger
        st.header("Pipeline Control")
        if st.button("🔄 Run Polling Cycle"):
            try:
                with st.spinner(
                    "Polling feeds & Generating summaries... (Max 5 items)"
                ):
                    feed_mgr.run_polling_cycle()
                st.success("Cycle Complete!")
                st.rerun()
            except Exception as e:
                st.error(f"Pipeline Error: {e}")

    # Main Content: Stats & Feed
    col1, col2 = st.columns(2)

    channels = channel_mgr.list_channels()
    summaries = crud.get_latest_summaries(db, limit=20)

    with col1:
        st.metric("Monitored Channels", len(channels))
    with col2:
        st.metric(
            "Total AI Summaries", len(summaries)
        )  # This logic is technically "Latest" length, but indicative for now.

    st.divider()

    # Tabbed View
    tab1, tab2 = st.tabs(["📢 Latest Feed", "📺 Channel List"])

    with tab1:
        if not summaries:
            st.info("No summaries generated yet. Add a channel and run the poller!")

        for item in summaries:
            with st.expander(f"{item.title}  |  {item.channel_id}", expanded=True):
                st.markdown(item.summary)
                st.caption(
                    f"Published: {item.published_at}  •  [Watch Video]({item.link})"
                )

    with tab2:
        if not channels:
            st.info("No channels found.")
        else:
            # Simple dataframe view
            data = [
                {
                    "Name": c.name or "Unknown",
                    "URL": c.url,
                    "Last Checked": c.last_checked,
                }
                for c in channels
            ]
            st.dataframe(data, use_container_width=True)


if __name__ == "__main__":
    main()
