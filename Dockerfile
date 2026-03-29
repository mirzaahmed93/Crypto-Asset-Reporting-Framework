FROM python:3.11

# HuggingFace Spaces requires a non-root user
RUN useradd -m -u 1000 user
USER user
ENV HOME=/home/user \
    PATH=/home/user/.local/bin:$PATH

WORKDIR $HOME/app

# Install dependencies
COPY --chown=user requirements.txt $HOME/app/
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application files
COPY --chown=user . $HOME/app/

# Expose the standard HuggingFace port
EXPOSE 7860

# Launch Voila dashboard safely
CMD ["voila", "--port=7860", "--no-browser", "--theme=dark", "--Voila.ip=0.0.0.0", "lp_reconciliation.ipynb"]
