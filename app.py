st.markdown(
    """
    <style>
    .main-title {
        font-size: 42px;
        font-weight: 800;
        margin-bottom: 0px;
        color: #FFFFFF;
    }

    .subtitle {
        font-size: 17px;
        color: #D1D5DB;
        margin-bottom: 25px;
    }

    .small-muted {
        font-size: 13px;
        color: #D1D5DB;
    }

    .simulation-card {
        background-color: #111827;
        border: 1px solid #374151;
        border-radius: 16px;
        padding: 24px;
        margin-top: 10px;
        margin-bottom: 20px;
        color: #F9FAFB;
    }

    .recommended-card {
        background-color: #052E16;
        border: 1px solid #16A34A;
        border-radius: 16px;
        padding: 20px;
        margin-top: 10px;
        margin-bottom: 20px;
        color: #F9FAFB;
    }

    .freshness-card {
        background-color: #422006;
        border: 1px solid #F59E0B;
        border-radius: 16px;
        padding: 18px;
        margin-top: 10px;
        margin-bottom: 20px;
        color: #FFFFFF;
    }

    .freshness-card .card-title {
        color: #FFFFFF;
    }

    .freshness-card .card-line {
        color: #FFFFFF;
    }

    .card-title {
        font-size: 22px;
        font-weight: 700;
        margin-bottom: 10px;
        color: #F9FAFB;
    }

    .card-line {
        font-size: 15px;
        margin-bottom: 6px;
        color: #F9FAFB;
    }

    .highlight-card {
        background-color: #0F172A;
        border: 1px solid #334155;
        border-radius: 16px;
        padding: 20px;
        min-height: 155px;
        margin-bottom: 10px;
        color: #F9FAFB;
    }

    .highlight-icon {
        font-size: 26px;
        margin-bottom: 8px;
        color: #F9FAFB;
    }

    .highlight-title {
        font-size: 17px;
        font-weight: 700;
        margin-bottom: 8px;
        color: #F9FAFB;
    }

    .highlight-text {
        font-size: 14px;
        color: #E5E7EB;
        line-height: 1.45;
    }

    .footer-box {
        background-color: #0F172A;
        border: 1px solid #334155;
        border-radius: 14px;
        padding: 16px;
        margin-top: 20px;
        color: #F9FAFB;
    }

    .footer-box .small-muted {
        color: #D1D5DB;
    }

    a {
        text-decoration: none;
        color: #60A5FA;
    }

    a:hover {
        text-decoration: underline;
    }

    @media (prefers-color-scheme: light) {
        .main-title {
            color: #111827;
        }

        .subtitle {
            color: #374151;
        }

        .simulation-card {
            background-color: #F9FAFB;
            border: 1px solid #D1D5DB;
            color: #111827;
        }

        .simulation-card .card-title,
        .simulation-card .card-line {
            color: #111827;
        }

        .recommended-card {
            background-color: #ECFDF5;
            border: 1px solid #16A34A;
            color: #064E3B;
        }

        .recommended-card .card-title,
        .recommended-card .card-line {
            color: #064E3B;
        }

        .freshness-card {
            background-color: #78350F;
            border: 1px solid #D97706;
            color: #FFFFFF;
        }

        .freshness-card .card-title,
        .freshness-card .card-line {
            color: #FFFFFF;
        }

        .highlight-card {
            background-color: #F8FAFC;
            border: 1px solid #CBD5E1;
            color: #111827;
        }

        .highlight-icon,
        .highlight-title {
            color: #111827;
        }

        .highlight-text {
            color: #374151;
        }

        .footer-box {
            background-color: #F8FAFC;
            border: 1px solid #CBD5E1;
            color: #111827;
        }

        .footer-box .small-muted {
            color: #374151;
        }

        a {
            color: #2563EB;
        }
    }
    </style>
    """,
    unsafe_allow_html=True,
)
