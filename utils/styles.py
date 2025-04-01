def get_css():
    return """
    /* Two-column layout */
    .column-container {
        display: flex;
        gap: 2rem;
        align-items: flex-start;
    }
    
    .column-left {
        flex: 1;
        max-width: 400px;
    }
    
    .column-right {
        flex: 2;
    }
    
    /* Card spacing */
    .card {
        margin-bottom: 1rem;
        padding: 1rem;
    }
    
    /* Metadata styles */
    .metadata {
        font-size: 0.9rem;
        padding-top: 0.75rem;
        border-top: 1px solid rgba(0, 0, 0, 0.1);
    }
    """ 