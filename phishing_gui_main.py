"""
Phishing Detection GUI Application - Main Dashboard
Beautiful purple and white themed interface with login, tabs, and visualizations.
"""

import customtkinter as ctk
from tkinter import filedialog, messagebox
import pandas as pd
import joblib
from pathlib import Path
import threading
from feature_extractor import FeatureExtractor
from user_auth import UserAuth
from auto_trainer import AutoTrainer
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import numpy as np
from datetime import datetime
import os


class PhishingDetectionDashboard:
    def __init__(self, root, username):
        self.root = root
        self.username = username
        self.auth = UserAuth()
        
        self.root.title(f"Phishing Email Detector - {username}")
        self.root.geometry("1400x900")
        
        # Set custom theme with purple and white
        ctk.set_appearance_mode("light")
        ctk.set_default_color_theme("blue")
        
        # Colors - Purple and White Theme
        self.colors = {
            'primary': '#8B5CF6',
            'primary_dark': '#6D28D9',
            'primary_light': '#A78BFA',
            'secondary': '#F3F4F6',
            'accent': '#EC4899',
            'text': '#1F2937',
            'text_light': '#6B7280',
            'success': '#10B981',
            'danger': '#EF4444',
            'white': '#FFFFFF',
            'bg': '#F5F3FF'
        }
        
        # Data storage
        self.csv_data = None
        self.model = None
        self.model_path = None
        self.predictions = None
        self.current_session_results = None
        self.auto_trainer = AutoTrainer(callback=self.training_progress_callback)
        self.is_training = False
        
        # Set background
        self.root.configure(bg=self.colors['bg'])
        
        # Build UI
        self.create_widgets()
        
        # Load user stats
        self.load_user_stats()
    
    def create_widgets(self):
        """Create all GUI widgets."""
        # Main container
        main_container = ctk.CTkFrame(self.root, fg_color=self.colors['bg'])
        main_container.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Header section
        header_frame = ctk.CTkFrame(main_container, fg_color=self.colors['primary'], corner_radius=15)
        header_frame.pack(fill="x", pady=(0, 20))
        
        # Header content
        header_content = ctk.CTkFrame(header_frame, fg_color="transparent")
        header_content.pack(fill="x", padx=30, pady=20)
        
        title_label = ctk.CTkLabel(
            header_content,
            text="🔒 Phishing Email Detection System",
            font=ctk.CTkFont(size=28, weight="bold"),
            text_color=self.colors['white'],
            anchor="w"
        )
        title_label.pack(side="left", fill="x", expand=True)
        
        # User info and logout
        user_frame = ctk.CTkFrame(header_content, fg_color="transparent")
        user_frame.pack(side="right")
        
        user_label = ctk.CTkLabel(
            user_frame,
            text=f"👤 {self.username}",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=self.colors['white']
        )
        user_label.pack(side="left", padx=(0, 15))
        
        logout_btn = ctk.CTkButton(
            user_frame,
            text="Logout",
            command=self.logout,
            fg_color=self.colors['primary_dark'],
            hover_color="#5B21B6",
            font=ctk.CTkFont(size=12),
            width=80,
            height=30,
            corner_radius=8
        )
        logout_btn.pack(side="left")
        
        # Tab view for different sections
        self.tabview = ctk.CTkTabview(main_container, fg_color=self.colors['white'], corner_radius=15)
        self.tabview.pack(fill="both", expand=True)
        
        # Analysis Tab
        analysis_tab = self.tabview.add("📊 Analysis")
        self.create_analysis_tab(analysis_tab)
        
        # Results Graph Tab
        results_tab = self.tabview.add("📈 Results Summary")
        self.create_results_graph_tab(results_tab)
        
        # History Tab
        history_tab = self.tabview.add("📜 History")
        self.create_history_tab(history_tab)
    
    def create_analysis_tab(self, parent):
        """Create the main analysis tab."""
        # Content area with two columns
        content_frame = ctk.CTkFrame(parent, fg_color="transparent")
        content_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Left column - Controls
        left_frame = ctk.CTkFrame(content_frame, fg_color=self.colors['white'], corner_radius=15)
        left_frame.pack(side="left", fill="both", expand=True, padx=(0, 10))
        
        # Model selection
        model_frame = ctk.CTkFrame(left_frame, fg_color="transparent")
        model_frame.pack(fill="x", padx=20, pady=20)
        
        model_label = ctk.CTkLabel(
            model_frame,
            text="Model Selection",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color=self.colors['text']
        )
        model_label.pack(anchor="w", pady=(0, 10))
        
        self.model_status_label = ctk.CTkLabel(
            model_frame,
            text="No model loaded",
            font=ctk.CTkFont(size=12),
            text_color=self.colors['text_light']
        )
        self.model_status_label.pack(anchor="w", pady=(0, 10))
        
        load_model_btn = ctk.CTkButton(
            model_frame,
            text="📁 Load Model (.pkl)",
            command=self.load_model,
            fg_color=self.colors['primary'],
            hover_color=self.colors['primary_dark'],
            font=ctk.CTkFont(size=14, weight="bold"),
            height=40,
            corner_radius=10
        )
        load_model_btn.pack(fill="x", pady=(0, 20))
        
        # File upload section
        upload_frame = ctk.CTkFrame(left_frame, fg_color="transparent")
        upload_frame.pack(fill="x", padx=20, pady=20)
        
        upload_label = ctk.CTkLabel(
            upload_frame,
            text="CSV File Upload",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color=self.colors['text']
        )
        upload_label.pack(anchor="w", pady=(0, 10))
        
        self.file_status_label = ctk.CTkLabel(
            upload_frame,
            text="No file selected",
            font=ctk.CTkFont(size=12),
            text_color=self.colors['text_light']
        )
        self.file_status_label.pack(anchor="w", pady=(0, 10))
        
        upload_btn = ctk.CTkButton(
            upload_frame,
            text="📤 Upload Dataset (CSV/Excel)",
            command=self.upload_csv,
            fg_color=self.colors['primary'],
            hover_color=self.colors['primary_dark'],
            font=ctk.CTkFont(size=16, weight="bold"),
            height=50,
            corner_radius=12
        )
        upload_btn.pack(fill="x", pady=(0, 10))
        
        # Info label
        info_label = ctk.CTkLabel(
            upload_frame,
            text="💡 Tip: Upload a dataset with 'label' column to automatically train a model!",
            font=ctk.CTkFont(size=11),
            text_color=self.colors['text_light'],
            wraplength=300
        )
        info_label.pack(pady=(0, 20))
        
        # Predict button
        predict_btn = ctk.CTkButton(
            upload_frame,
            text="🔍 Analyze Emails",
            command=self.predict_emails,
            fg_color=self.colors['accent'],
            hover_color="#DB2777",
            font=ctk.CTkFont(size=16, weight="bold"),
            height=50,
            corner_radius=12,
            state="disabled"
        )
        predict_btn.pack(fill="x")
        self.predict_button = predict_btn
        
        # Progress bar
        self.progress_bar = ctk.CTkProgressBar(
            upload_frame,
            fg_color=self.colors['secondary'],
            progress_color=self.colors['primary']
        )
        self.progress_bar.pack(fill="x", pady=(20, 0))
        self.progress_bar.set(0)
        
        self.progress_label = ctk.CTkLabel(
            upload_frame,
            text="",
            font=ctk.CTkFont(size=12),
            text_color=self.colors['text_light']
        )
        self.progress_label.pack(pady=(5, 0))
        
        # Right column - Results
        right_frame = ctk.CTkFrame(content_frame, fg_color=self.colors['white'], corner_radius=15)
        right_frame.pack(side="right", fill="both", expand=True, padx=(10, 0))
        
        results_label = ctk.CTkLabel(
            right_frame,
            text="Results",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color=self.colors['text']
        )
        results_label.pack(anchor="w", padx=20, pady=20)
        
        # Scrollable text area for results
        self.results_text = ctk.CTkTextbox(
            right_frame,
            font=ctk.CTkFont(size=12),
            fg_color=self.colors['secondary'],
            text_color=self.colors['text'],
            corner_radius=10,
            wrap="word"
        )
        self.results_text.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        
        # Export button
        export_btn = ctk.CTkButton(
            right_frame,
            text="💾 Export Results to CSV",
            command=self.export_results,
            fg_color=self.colors['success'],
            hover_color="#059669",
            font=ctk.CTkFont(size=14, weight="bold"),
            height=40,
            corner_radius=10,
            state="disabled"
        )
        export_btn.pack(fill="x", padx=20, pady=(0, 20))
        self.export_button = export_btn
    
    def create_results_graph_tab(self, parent):
        """Create tab with graph visualization."""
        # Container for graph
        graph_frame = ctk.CTkFrame(parent, fg_color="transparent")
        graph_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Title
        title_label = ctk.CTkLabel(
            graph_frame,
            text="Analysis Results Visualization",
            font=ctk.CTkFont(size=24, weight="bold"),
            text_color=self.colors['text']
        )
        title_label.pack(pady=(0, 20))
        
        # Graph container
        self.graph_container = ctk.CTkFrame(graph_frame, fg_color=self.colors['white'], corner_radius=15)
        self.graph_container.pack(fill="both", expand=True)
        
        # Placeholder text
        self.graph_placeholder = ctk.CTkLabel(
            self.graph_container,
            text="No analysis results yet.\nRun an analysis to see visualizations here.",
            font=ctk.CTkFont(size=16),
            text_color=self.colors['text_light']
        )
        self.graph_placeholder.pack(expand=True)
        
        self.graph_canvas = None
    
    def create_history_tab(self, parent):
        """Create history tab showing all previous uploads."""
        # Container
        history_frame = ctk.CTkFrame(parent, fg_color="transparent")
        history_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Title
        title_label = ctk.CTkLabel(
            history_frame,
            text="Analysis History",
            font=ctk.CTkFont(size=24, weight="bold"),
            text_color=self.colors['text']
        )
        title_label.pack(anchor="w", pady=(0, 20))
        
        # Scrollable frame for history
        scroll_frame = ctk.CTkScrollableFrame(
            history_frame,
            fg_color=self.colors['white'],
            corner_radius=15
        )
        scroll_frame.pack(fill="both", expand=True)
        
        self.history_scroll_frame = scroll_frame
        self.load_history()
    
    def load_user_stats(self):
        """Load and display user statistics."""
        stats = self.auth.get_user_stats(self.username)
        if stats:
            # Could display stats in header or sidebar
            pass
    
    def load_model(self):
        """Load a trained phishing detection model."""
        file_path = filedialog.askopenfilename(
            title="Select Model File",
            filetypes=[("Pickle files", "*.pkl"), ("All files", "*.*")]
        )
        
        if file_path:
            try:
                self.model = joblib.load(file_path)
                self.model_path = file_path
                model_name = Path(file_path).name
                self.model_status_label.configure(
                    text=f"Loaded: {model_name}",
                    text_color=self.colors['success']
                )
                messagebox.showinfo("Success", "Model loaded successfully!")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load model:\n{str(e)}")
                self.model_status_label.configure(
                    text="Error loading model",
                    text_color=self.colors['danger']
                )
    
    def upload_csv(self):
        """Upload and load CSV or Excel file."""
        file_path = filedialog.askopenfilename(
            title="Select Dataset File",
            filetypes=[
                ("All supported", "*.csv;*.xlsx;*.xls"),
                ("CSV files", "*.csv"),
                ("Excel files", "*.xlsx;*.xls"),
                ("All files", "*.*")
            ]
        )
        
        if file_path:
            try:
                # Load file based on extension
                file_ext = Path(file_path).suffix.lower()
                
                if file_ext == '.csv':
                    self.csv_data = pd.read_csv(file_path)
                elif file_ext in ['.xlsx', '.xls']:
                    self.csv_data = pd.read_excel(file_path)
                else:
                    messagebox.showerror("Error", "Unsupported file format. Please use CSV or Excel files.")
                    return
                
                # Check required columns
                required_cols = ['email_body', 'email_subject', 'from_address']
                missing_cols = [col for col in required_cols if col not in self.csv_data.columns]
                
                if missing_cols:
                    messagebox.showerror(
                        "Error",
                        f"Missing required columns: {', '.join(missing_cols)}\n\n"
                        f"Required columns: email_body, email_subject, from_address"
                    )
                    return
                
                file_name = Path(file_path).name
                row_count = len(self.csv_data)
                self.file_status_label.configure(
                    text=f"Loaded: {file_name} ({row_count} emails)",
                    text_color=self.colors['success']
                )
                
                # Check if this is training data (has 'label' column)
                is_training_data = 'label' in self.csv_data.columns
                
                if is_training_data:
                    # Ask user if they want to train automatically
                    response = messagebox.askyesno(
                        "Training Data Detected",
                        f"Dataset contains 'label' column - this appears to be training data.\n\n"
                        f"Would you like to automatically train a model in the background?\n\n"
                        f"This will create a new model file for you to use."
                    )
                    
                    if response:
                        # Start automatic training in background
                        self.start_auto_training(file_path)
                else:
                    # Regular analysis data
                    # Enable predict button if model is loaded
                    if self.model:
                        self.predict_button.configure(state="normal")
                    
                    # Display preview
                    self.display_csv_preview()
                    
                    messagebox.showinfo(
                        "Success",
                        f"File loaded successfully!\n{row_count} emails found.\n\n"
                        f"Load a model to start analyzing, or upload a dataset with 'label' column to train a new model."
                    )
                
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load file:\n{str(e)}")
                self.file_status_label.configure(
                    text="Error loading file",
                    text_color=self.colors['danger']
                )
    
    def start_auto_training(self, file_path):
        """Start automatic training in background."""
        if self.is_training:
            messagebox.showwarning("Warning", "Training already in progress. Please wait.")
            return
        
        self.is_training = True
        self.predict_button.configure(state="disabled")
        
        # Show training notification
        self.file_status_label.configure(
            text="Training model in background...",
            text_color=self.colors['primary']
        )
        
        # Start training in background thread
        thread = threading.Thread(target=self._train_in_background, args=(file_path,))
        thread.daemon = True
        thread.start()
    
    def training_progress_callback(self, message, progress):
        """Callback for training progress updates."""
        self.root.after(0, lambda: self.progress_label.configure(text=message))
        self.root.after(0, lambda: self.progress_bar.set(progress / 100))
    
    def _train_in_background(self, file_path):
        """Train model in background thread."""
        try:
            # Use the loaded data
            df = self.csv_data.copy()
            
            # Generate output path
            file_name = Path(file_path).stem
            output_dir = Path("trained_models")
            output_dir.mkdir(exist_ok=True)
            output_path = output_dir / f"{file_name}_model_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pkl"
            
            # Train model
            result = self.auto_trainer.train_model_auto(
                df,
                output_path=str(output_path),
                model_type='auto',
                test_size=0.2
            )
            
            # Load the trained model
            self.model = joblib.load(str(output_path))
            self.model_path = str(output_path)
            
            # Update UI
            self.root.after(0, lambda: self.model_status_label.configure(
                text=f"Auto-trained: {Path(output_path).name} ({result['accuracy']:.2%} accuracy)",
                text_color=self.colors['success']
            ))
            
            self.root.after(0, lambda: self.file_status_label.configure(
                text=f"Model trained successfully! ({result['accuracy']:.2%} accuracy)",
                text_color=self.colors['success']
            ))
            
            self.root.after(0, lambda: self.predict_button.configure(state="normal"))
            self.root.after(0, lambda: self.progress_label.configure(text="Training complete!"))
            self.root.after(0, lambda: self.progress_bar.set(0))
            
            self.root.after(0, lambda: messagebox.showinfo(
                "Training Complete!",
                f"Model trained successfully!\n\n"
                f"Accuracy: {result['accuracy']:.2%}\n"
                f"Model Type: {result['model_type']}\n"
                f"Saved to: {output_path}\n\n"
                f"You can now analyze emails with this model!"
            ))
            
            # Display preview
            self.root.after(0, self.display_csv_preview)
            
        except Exception as e:
            self.root.after(0, lambda: messagebox.showerror(
                "Training Error",
                f"Failed to train model:\n{str(e)}"
            ))
            self.root.after(0, lambda: self.file_status_label.configure(
                text="Training failed",
                text_color=self.colors['danger']
            ))
        finally:
            self.is_training = False
    
    def display_csv_preview(self):
        """Display a preview of the loaded CSV data."""
        if self.csv_data is not None:
            preview_text = f"📊 CSV Preview ({len(self.csv_data)} emails)\n"
            preview_text += "=" * 50 + "\n\n"
            
            # Show first 5 rows
            for idx, row in self.csv_data.head(5).iterrows():
                preview_text += f"Email {idx + 1}:\n"
                preview_text += f"  Subject: {str(row.get('email_subject', 'N/A'))[:50]}...\n"
                preview_text += f"  From: {str(row.get('from_address', 'N/A'))}\n\n"
            
            if len(self.csv_data) > 5:
                preview_text += f"... and {len(self.csv_data) - 5} more emails\n"
            
            self.results_text.delete("1.0", "end")
            self.results_text.insert("1.0", preview_text)
    
    def predict_emails(self):
        """Run predictions on uploaded emails."""
        if self.csv_data is None:
            messagebox.showwarning("Warning", "Please upload a CSV file first!")
            return
        
        if self.model is None:
            messagebox.showwarning("Warning", "Please load a model first!")
            return
        
        # Disable button during prediction
        self.predict_button.configure(state="disabled")
        self.progress_bar.set(0)
        self.progress_label.configure(text="Analyzing emails...")
        self.root.update()
        
        # Run prediction in separate thread
        thread = threading.Thread(target=self._predict_thread)
        thread.daemon = True
        thread.start()
    
    def _predict_thread(self):
        """Run prediction in background thread."""
        try:
            feature_extractor = self.model.get('feature_extractor', FeatureExtractor())
            scaler = self.model.get('scaler')
            model = self.model['model']
            feature_names = self.model.get('feature_names')
            
            predictions_list = []
            total = len(self.csv_data)
            
            for idx, row in self.csv_data.iterrows():
                # Update progress
                progress = (idx + 1) / total
                self.root.after(0, lambda p=progress: self.progress_bar.set(p))
                self.root.after(0, lambda i=idx+1, t=total: 
                    self.progress_label.configure(text=f"Processing email {i}/{t}..."))
                
                # Prepare email data
                email_data = {
                    'email_body': str(row.get('email_body', '')),
                    'email_subject': str(row.get('email_subject', '')),
                    'from_address': str(row.get('from_address', '')),
                    'to_address': str(row.get('to_address', '')),
                    'reply_to': str(row.get('reply_to', '')),
                    'urls': str(row.get('urls', '')),
                }
                
                # Extract features and predict
                features = feature_extractor.extract_features(email_data)
                features_df = pd.DataFrame([features])
                
                if feature_names:
                    for col in feature_names:
                        if col not in features_df.columns:
                            features_df[col] = 0
                    features_df = features_df[feature_names]
                
                features_df = features_df.fillna(0)
                
                if scaler:
                    features_df = pd.DataFrame(scaler.transform(features_df), columns=features_df.columns)
                
                prediction = model.predict(features_df)[0]
                probability = model.predict_proba(features_df)[0][1] if hasattr(model, 'predict_proba') else None
                
                predictions_list.append({
                    'is_phishing': int(prediction),
                    'label': 'Phishing' if prediction == 1 else 'Legitimate',
                    'confidence': float(probability) if probability is not None else None
                })
            
            # Store predictions
            self.predictions = pd.DataFrame(predictions_list)
            
            # Calculate session stats
            phishing_count = self.predictions['is_phishing'].sum()
            legitimate_count = len(self.predictions) - phishing_count
            
            # Save session
            csv_filename = 'Unknown'
            file_status_text = self.file_status_label.cget('text')
            if ':' in file_status_text:
                try:
                    csv_filename = file_status_text.split(': ')[-1].split(' (')[0]
                except:
                    csv_filename = 'Unknown'
            
            self.auth.add_session(self.username, {
                'total_emails': total,
                'phishing_count': int(phishing_count),
                'legitimate_count': int(legitimate_count),
                'model_used': Path(self.model_path).name if self.model_path else 'Unknown',
                'csv_filename': csv_filename
            })
            
            # Store current session results
            self.current_session_results = {
                'total': total,
                'phishing': int(phishing_count),
                'legitimate': int(legitimate_count),
                'predictions': self.predictions
            }
            
            # Update UI
            self.root.after(0, self.display_results)
            self.root.after(0, self.update_graph)
            self.root.after(0, self.load_history)
            self.root.after(0, lambda: self.progress_label.configure(text="Analysis complete!"))
            self.root.after(0, lambda: self.predict_button.configure(state="normal"))
            self.root.after(0, lambda: self.export_button.configure(state="normal"))
            
        except Exception as e:
            self.root.after(0, lambda: messagebox.showerror("Error", f"Prediction failed:\n{str(e)}"))
            self.root.after(0, lambda: self.predict_button.configure(state="normal"))
            self.root.after(0, lambda: self.progress_label.configure(text="Error occurred"))
    
    def display_results(self):
        """Display prediction results."""
        if self.predictions is None or self.csv_data is None:
            return
        
        results_df = self.csv_data.copy()
        results_df['Prediction'] = self.predictions['label']
        results_df['Confidence'] = self.predictions['confidence'].apply(
            lambda x: f"{x:.2%}" if x is not None else "N/A"
        )
        results_df['Is_Phishing'] = self.predictions['is_phishing']
        
        total = len(results_df)
        phishing_count = results_df['Is_Phishing'].sum()
        legitimate_count = total - phishing_count
        
        results_text = "🔍 ANALYSIS RESULTS\n"
        results_text += "=" * 60 + "\n\n"
        results_text += f"📧 Total Emails Analyzed: {total}\n"
        results_text += f"🔴 Phishing Detected: {phishing_count} ({phishing_count/total*100:.1f}%)\n"
        results_text += f"🟢 Legitimate: {legitimate_count} ({legitimate_count/total*100:.1f}%)\n\n"
        results_text += "=" * 60 + "\n\n"
        
        for idx, row in results_df.iterrows():
            result_emoji = "🔴" if row['Is_Phishing'] == 1 else "🟢"
            results_text += f"{result_emoji} Email {idx + 1}\n"
            results_text += f"   Subject: {str(row.get('email_subject', 'N/A'))[:60]}...\n"
            results_text += f"   From: {row.get('from_address', 'N/A')}\n"
            results_text += f"   Prediction: {row['Prediction']}\n"
            results_text += f"   Confidence: {row['Confidence']}\n\n"
        
        self.results_text.delete("1.0", "end")
        self.results_text.insert("1.0", results_text)
        
        self.results_df = results_df
    
    def update_graph(self):
        """Update the results graph tab with visualization."""
        if self.current_session_results is None:
            return
        
        # Clear placeholder
        if self.graph_placeholder:
            self.graph_placeholder.destroy()
            self.graph_placeholder = None
        
        # Clear existing canvas
        if self.graph_canvas:
            self.graph_canvas.get_tk_widget().destroy()
        
        # Create figure
        fig = Figure(figsize=(10, 6), facecolor='white')
        ax = fig.add_subplot(111)
        
        # Data
        labels = ['Phishing', 'Legitimate']
        sizes = [
            self.current_session_results['phishing'],
            self.current_session_results['legitimate']
        ]
        colors = [self.colors['danger'], self.colors['success']]
        explode = (0.05, 0)  # Slight explode for phishing
        
        # Create pie chart
        if sum(sizes) > 0:
            ax.pie(sizes, explode=explode, labels=labels, colors=colors,
                   autopct='%1.1f%%', shadow=True, startangle=90,
                   textprops={'fontsize': 12, 'weight': 'bold'})
        else:
            ax.text(0.5, 0.5, 'No data to display', ha='center', va='center', 
                   fontsize=14, transform=ax.transAxes)
        ax.set_title('Email Classification Results', fontsize=16, fontweight='bold', pad=20)
        
        # Create bar chart below
        fig2 = Figure(figsize=(10, 4), facecolor='white')
        ax2 = fig2.add_subplot(111)
        
        if sum(sizes) > 0:
            bars = ax2.bar(labels, sizes, color=colors, alpha=0.8, edgecolor='black', linewidth=2)
            ax2.set_ylabel('Number of Emails', fontsize=12, fontweight='bold')
            ax2.set_title('Email Count by Category', fontsize=14, fontweight='bold')
            ax2.grid(axis='y', alpha=0.3)
            
            # Add value labels on bars
            for bar in bars:
                height = bar.get_height()
                if height > 0:
                    ax2.text(bar.get_x() + bar.get_width()/2., height,
                            f'{int(height)}',
                            ha='center', va='bottom', fontsize=12, fontweight='bold')
        else:
            ax2.text(0.5, 0.5, 'No data to display', ha='center', va='center',
                    fontsize=14, transform=ax2.transAxes)
        
        # Embed in tkinter
        canvas1 = FigureCanvasTkAgg(fig, self.graph_container)
        canvas1.draw()
        canvas1.get_tk_widget().pack(fill="both", expand=True, padx=20, pady=20)
        
        canvas2 = FigureCanvasTkAgg(fig2, self.graph_container)
        canvas2.draw()
        canvas2.get_tk_widget().pack(fill="both", expand=True, padx=20, pady=(0, 20))
        
        self.graph_canvas = canvas1
    
    def load_history(self):
        """Load and display analysis history."""
        # Clear existing widgets
        for widget in self.history_scroll_frame.winfo_children():
            widget.destroy()
        
        sessions = self.auth.get_session_history(self.username)
        
        if not sessions:
            no_history_label = ctk.CTkLabel(
                self.history_scroll_frame,
                text="No analysis history yet.\nRun your first analysis to see history here.",
                font=ctk.CTkFont(size=16),
                text_color=self.colors['text_light']
            )
            no_history_label.pack(pady=50)
            return
        
        # Display sessions (most recent first)
        for session in reversed(sessions):
            session_frame = ctk.CTkFrame(
                self.history_scroll_frame,
                fg_color=self.colors['white'],
                corner_radius=10
            )
            session_frame.pack(fill="x", padx=10, pady=10)
            
            # Session info
            timestamp = datetime.fromisoformat(session['timestamp']).strftime("%Y-%m-%d %H:%M:%S")
            
            info_text = f"📅 {timestamp}\n"
            info_text += f"📧 Total Emails: {session['total_emails']}\n"
            info_text += f"🔴 Phishing: {session['phishing_count']} ({session['phishing_count']/session['total_emails']*100:.1f}%)\n"
            info_text += f"🟢 Legitimate: {session['legitimate_count']} ({session['legitimate_count']/session['total_emails']*100:.1f}%)\n"
            info_text += f"🤖 Model: {session.get('model_used', 'Unknown')}\n"
            info_text += f"📁 File: {session.get('csv_filename', 'Unknown')}"
            
            session_label = ctk.CTkLabel(
                session_frame,
                text=info_text,
                font=ctk.CTkFont(size=12),
                text_color=self.colors['text'],
                anchor="w",
                justify="left"
            )
            session_label.pack(fill="x", padx=20, pady=15)
    
    def export_results(self):
        """Export results to CSV file."""
        if not hasattr(self, 'results_df') or self.results_df is None:
            messagebox.showwarning("Warning", "No results to export!")
            return
        
        file_path = filedialog.asksaveasfilename(
            title="Save Results",
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
        )
        
        if file_path:
            try:
                self.results_df.to_csv(file_path, index=False)
                messagebox.showinfo("Success", f"Results exported to:\n{file_path}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to export results:\n{str(e)}")
    
    def logout(self):
        """Logout and return to login window."""
        if messagebox.askyesno("Logout", "Are you sure you want to logout?"):
            self.root.destroy()
            # Restart application
            import app
            import sys
            sys.exit(0)
            # Note: User should restart app.py manually or use subprocess

