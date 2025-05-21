import React from "react";

interface SubmitProps {
    label?: string
}

const Submit: React.FC<SubmitProps & { isLoading: boolean }> = ({ label = "Submit", isLoading = false }) => (
    <button
    type="submit"
    disabled={isLoading}
    style={{
        backgroundColor: "transparent",
        color: "white",
        border: "none",
        padding: "0.5rem 1rem",
        borderRadius: "0.25rem",
        boxShadow: "0px 0px 30px #28a745 inset"
    }}>
        {label}
    </button>
);

export default Submit;