import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.linear_model import LinearRegression, Ridge, Lasso
from sklearn.svm import SVR
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score, mean_absolute_percentage_error
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.model_selection import train_test_split, cross_val_score, GridSearchCV
from sklearn.feature_selection import SelectKBest, f_regression
import joblib
import warnings
warnings.filterwarnings('ignore')

class EVSalesForecaster:
    def __init__(self):
        self.models = {}
        self.scalers = {}
        self.encoders = {}
        self.feature_selector = None
        self.best_model = None
        self.best_model_name = None
        self.feature_columns = []
        self.target_column = 'sales_amount'
        
    def prepare_features(self, df):
        """Prepare features for machine learning models"""
        df = df.copy()
        
        # Time-based features
        df['year'] = df['date'].dt.year
        df['month'] = df['date'].dt.month
        df['quarter'] = df['date'].dt.quarter
        df['day_of_year'] = df['date'].dt.dayofyear
        df['week_of_year'] = df['date'].dt.isocalendar().week
        
        # Cyclical features
        df['month_sin'] = np.sin(2 * np.pi * df['month'] / 12)
        df['month_cos'] = np.cos(2 * np.pi * df['month'] / 12)
        df['quarter_sin'] = np.sin(2 * np.pi * df['quarter'] / 4)
        df['quarter_cos'] = np.cos(2 * np.pi * df['quarter'] / 4)
        
        # Lag features
        df = df.sort_values(['state', 'date'])
        for lag in [1, 2, 3, 6, 12]:
            df[f'sales_lag_{lag}'] = df.groupby('state')['sales_amount'].shift(lag)
        
        # Rolling window features
        for window in [3, 6, 12]:
            df[f'sales_rolling_mean_{window}'] = df.groupby('state')['sales_amount'].transform(
                lambda x: x.rolling(window=window, min_periods=1).mean()
            )
            df[f'sales_rolling_std_{window}'] = df.groupby('state')['sales_amount'].transform(
                lambda x: x.rolling(window=window, min_periods=1).std()
            )
        
        # Growth features
        df['sales_growth_1m'] = df.groupby('state')['sales_amount'].pct_change(1)
        df['sales_growth_3m'] = df.groupby('state')['sales_amount'].pct_change(3)
        df['sales_growth_12m'] = df.groupby('state')['sales_amount'].pct_change(12)
        
        # Market features
        df['ev_density'] = df['sales_amount'] / df['total_population']
        df['stations_per_1000_ev'] = df['total_stations'] / (df['sales_amount'] / 1000)
        df['price_per_kwh'] = df['price_avg'] / df['battery_capacity']
        
        # Handle categorical variables
        if 'state' in df.columns:
            le_state = LabelEncoder()
            df['state_encoded'] = le_state.fit_transform(df['state'].astype(str))
            self.encoders['state'] = le_state
            
        if 'manufacturer' in df.columns:
            le_manufacturer = LabelEncoder()
            df['manufacturer_encoded'] = le_manufacturer.fit_transform(df['manufacturer'].astype(str))
            self.encoders['manufacturer'] = le_manufacturer
            
        if 'vehicle_category' in df.columns:
            le_category = LabelEncoder()
            df['category_encoded'] = le_category.fit_transform(df['vehicle_category'].astype(str))
            self.encoders['vehicle_category'] = le_category
        
        return df
    
    def select_features(self, df):
        """Select the most important features for modeling"""
        # Define potential feature columns
        potential_features = [
            'year', 'month', 'quarter', 'day_of_year', 'week_of_year',
            'month_sin', 'month_cos', 'quarter_sin', 'quarter_cos',
            'sales_lag_1', 'sales_lag_2', 'sales_lag_3', 'sales_lag_6', 'sales_lag_12',
            'sales_rolling_mean_3', 'sales_rolling_mean_6', 'sales_rolling_mean_12',
            'sales_rolling_std_3', 'sales_rolling_std_6', 'sales_rolling_std_12',
            'sales_growth_1m', 'sales_growth_3m', 'sales_growth_12m',
            'ev_penetration_rate', 'gdp_per_capita', 'gasoline_price',
            'total_stations', 'stations_per_1000_ev', 'ev_density',
            'price_avg', 'battery_capacity', 'charging_time', 'price_per_kwh'
        ]
        
        # Add encoded categorical features
        if 'state_encoded' in df.columns:
            potential_features.append('state_encoded')
        if 'manufacturer_encoded' in df.columns:
            potential_features.append('manufacturer_encoded')
        if 'category_encoded' in df.columns:
            potential_features.append('category_encoded')
        
        # Filter to available features
        available_features = [col for col in potential_features if col in df.columns]
        
        # Remove features with too many missing values
        feature_data = df[available_features].fillna(0)
        missing_threshold = 0.3
        valid_features = []
        
        for col in available_features:
            missing_ratio = df[col].isnull().sum() / len(df)
            if missing_ratio <= missing_threshold:
                valid_features.append(col)
        
        # Feature selection using statistical tests
        X = feature_data[valid_features].fillna(0)
        y = df[self.target_column].fillna(0)
        
        selector = SelectKBest(score_func=f_regression, k=min(20, len(valid_features)))
        selector.fit(X, y)
        
        # Get selected features
        selected_features = [valid_features[i] for i in selector.get_support(indices=True)]
        self.feature_columns = selected_features
        self.feature_selector = selector
        
        return selected_features
    
    def train_models(self, df, test_size=0.2):
        """Train multiple machine learning models"""
        # Prepare features
        df_prepared = self.prepare_features(df)
        
        # Select features
        selected_features = self.select_features(df_prepared)
        
        # Prepare training data
        X = df_prepared[selected_features].fillna(0)
        y = df_prepared[self.target_column].fillna(0)
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=test_size, random_state=42, shuffle=False
        )
        
        # Scale features
        scaler = StandardScaler()
        X_train_scaled = scaler.fit_transform(X_train)
        X_test_scaled = scaler.transform(X_test)
        self.scalers['main'] = scaler
        
        # Define models
        models = {
            'linear_regression': LinearRegression(),
            'ridge_regression': Ridge(alpha=1.0),
            'lasso_regression': Lasso(alpha=1.0),
            'random_forest': RandomForestRegressor(
                n_estimators=100,
                max_depth=10,
                min_samples_split=5,
                min_samples_leaf=2,
                random_state=42
            ),
            'gradient_boosting': GradientBoostingRegressor(
                n_estimators=100,
                learning_rate=0.1,
                max_depth=6,
                random_state=42
            ),
            'svr': SVR(kernel='rbf', C=1.0, gamma='scale')
        }
        
        # Train models and evaluate
        model_performance = {}
        
        for name, model in models.items():
            print(f"Training {name}...")
            
            # Train model
            if name in ['linear_regression', 'ridge_regression', 'lasso_regression']:
                model.fit(X_train_scaled, y_train)
                y_pred = model.predict(X_test_scaled)
            else:
                model.fit(X_train, y_train)
                y_pred = model.predict(X_test)
            
            # Calculate metrics
            mae = mean_absolute_error(y_test, y_pred)
            rmse = np.sqrt(mean_squared_error(y_test, y_pred))
            r2 = r2_score(y_test, y_pred)
            mape = mean_absolute_percentage_error(y_test, y_pred) * 100
            
            # Cross-validation
            if name in ['linear_regression', 'ridge_regression', 'lasso_regression']:
                cv_scores = cross_val_score(model, X_train_scaled, y_train, cv=5, scoring='r2')
            else:
                cv_scores = cross_val_score(model, X_train, y_train, cv=5, scoring='r2')
            
            model_performance[name] = {
                'model': model,
                'mae': mae,
                'rmse': rmse,
                'r2': r2,
                'mape': mape,
                'cv_score_mean': cv_scores.mean(),
                'cv_score_std': cv_scores.std()
            }
            
            self.models[name] = model
        
        # Find best model
        best_score = -np.inf
        for name, performance in model_performance.items():
            if performance['r2'] > best_score:
                best_score = performance['r2']
                self.best_model = performance['model']
                self.best_model_name = name
        
        return model_performance
    
    def evaluate_models(self, X_test, y_test):
        """Evaluate all trained models"""
        results = {}
        
        for name, model in self.models.items():
            # Make predictions
            if name in ['linear_regression', 'ridge_regression', 'lasso_regression']:
                X_test_scaled = self.scalers['main'].transform(X_test)
                y_pred = model.predict(X_test_scaled)
            else:
                y_pred = model.predict(X_test)
            
            # Calculate metrics
            results[name] = {
                'mae': mean_absolute_error(y_test, y_pred),
                'rmse': np.sqrt(mean_squared_error(y_test, y_pred)),
                'r2': r2_score(y_test, y_pred),
                'mape': mean_absolute_percentage_error(y_test, y_pred) * 100
            }
        
        return results
    
    def predict_future(self, df, periods=12, model_name=None):
        """Make future predictions"""
        if model_name is None:
            model_name = self.best_model_name
            model = self.best_model
        else:
            model = self.models[model_name]
        
        # Create future dates
        last_date = df['date'].max()
        future_dates = pd.date_range(
            start=last_date + pd.DateOffset(months=1),
            periods=periods,
            freq='M'
        )
        
        predictions = []
        
        for date in future_dates:
            # Create feature row for future date
            future_row = {
                'date': date,
                'year': date.year,
                'month': date.month,
                'quarter': date.quarter,
                'day_of_year': date.dayofyear,
                'week_of_year': date.isocalendar().week,
                'month_sin': np.sin(2 * np.pi * date.month / 12),
                'month_cos': np.cos(2 * np.pi * date.month / 12),
                'quarter_sin': np.sin(2 * np.pi * date.quarter / 4),
                'quarter_cos': np.cos(2 * np.pi * date.quarter / 4)
            }
            
            # Use average values for other features
            for col in self.feature_columns:
                if col not in future_row:
                    if col in df.columns:
                        future_row[col] = df[col].mean()
                    else:
                        future_row[col] = 0
            
            # Create DataFrame and predict
            future_df = pd.DataFrame([future_row])
            
            # Prepare features
            future_df_prepared = self.prepare_features(future_df)
            
            # Select features
            X_future = future_df_prepared[self.feature_columns].fillna(0)
            
            # Scale if necessary
            if model_name in ['linear_regression', 'ridge_regression', 'lasso_regression']:
                X_future_scaled = self.scalers['main'].transform(X_future)
                prediction = model.predict(X_future_scaled)[0]
            else:
                prediction = model.predict(X_future)[0]
            
            predictions.append(max(0, prediction))  # Ensure non-negative
        
        return {
            'dates': future_dates,
            'predictions': predictions,
            'model_name': model_name
        }
    
    def get_feature_importance(self, model_name=None):
        """Get feature importance from tree-based models"""
        if model_name is None:
            model_name = self.best_model_name
        
        model = self.models[model_name]
        
        if hasattr(model, 'feature_importances_'):
            importance_df = pd.DataFrame({
                'feature': self.feature_columns,
                'importance': model.feature_importances_
            }).sort_values('importance', ascending=False)
            
            return importance_df
        else:
            return None
    
    def save_models(self, path='models/'):
        """Save trained models"""
        import os
        os.makedirs(path, exist_ok=True)
        
        # Save models
        for name, model in self.models.items():
            joblib.dump(model, f'{path}{name}.pkl')
        
        # Save scalers and encoders
        joblib.dump(self.scalers, f'{path}scalers.pkl')
        joblib.dump(self.encoders, f'{path}encoders.pkl')
        joblib.dump(self.feature_selector, f'{path}feature_selector.pkl')
        
        # Save feature columns
        with open(f'{path}feature_columns.txt', 'w') as f:
            f.write(','.join(self.feature_columns))
        
        # Save best model info
        with open(f'{path}best_model.txt', 'w') as f:
            f.write(self.best_model_name)
    
    def load_models(self, path='models/'):
        """Load trained models"""
        # Load feature columns
        with open(f'{path}feature_columns.txt', 'r') as f:
            self.feature_columns = f.read().split(',')
        
        # Load best model info
        with open(f'{path}best_model.txt', 'r') as f:
            self.best_model_name = f.read()
        
        # Load models
        for name in ['linear_regression', 'ridge_regression', 'lasso_regression', 
                    'random_forest', 'gradient_boosting', 'svr']:
            try:
                self.models[name] = joblib.load(f'{path}{name}.pkl')
            except:
                continue
        
        # Load scalers and encoders
        self.scalers = joblib.load(f'{path}scalers.pkl')
        self.encoders = joblib.load(f'{path}encoders.pkl')
        self.feature_selector = joblib.load(f'{path}feature_selector.pkl')
        
        # Set best model
        self.best_model = self.models[self.best_model_name]

class EVMarketSegmenter:
    def __init__(self):
        self.scaler = StandardScaler()
        self.kmeans = None
        self.segment_labels = {
            0: 'Emerging Markets',
            1: 'Growth Markets', 
            2: 'Mature Markets',
            3: 'Premium Markets'
        }
    
    def segment_states(self, df, n_clusters=4):
        """Segment states based on market characteristics"""
        # Prepare features for clustering
        state_features = df.groupby('state').agg({
            'sales_amount': 'sum',
            'revenue': 'sum',
            'ev_penetration_rate': 'mean',
            'gdp_per_capita': 'mean',
            'total_stations': 'mean',
            'stations_per_1000_ev': 'mean',
            'ev_density': 'mean',
            'price_avg': 'mean'
        }).reset_index()
        
        # Select features for clustering
        clustering_features = [
            'sales_amount', 'ev_penetration_rate', 'gdp_per_capita',
            'total_stations', 'ev_density', 'price_avg'
        ]
        
        X = state_features[clustering_features].fillna(0)
        
        # Scale features
        X_scaled = self.scaler.fit_transform(X)
        
        # Perform K-means clustering
        self.kmeans = KMeans(n_clusters=n_clusters, random_state=42)
        segments = self.kmeans.fit_predict(X_scaled)
        
        state_features['market_segment'] = segments
        state_features['segment_name'] = state_features['market_segment'].map(self.segment_labels)
        
        return state_features, X_scaled
    
    def get_segment_insights(self, state_features):
        """Get insights for each market segment"""
        segment_insights = {}
        
        for segment in state_features['market_segment'].unique():
            segment_data = state_features[state_features['market_segment'] == segment]
            
            segment_insights[segment] = {
                'segment_name': self.segment_labels[segment],
                'states': segment_data['state'].tolist(),
                'avg_sales': segment_data['sales_amount'].mean(),
                'avg_penetration': segment_data['ev_penetration_rate'].mean(),
                'avg_gdp_per_capita': segment_data['gdp_per_capita'].mean(),
                'avg_infrastructure': segment_data['total_stations'].mean(),
                'avg_price': segment_data['price_avg'].mean(),
                'characteristics': self._describe_segment(segment_data)
            }
        
        return segment_insights
    
    def _describe_segment(self, segment_data):
        """Describe segment characteristics"""
        characteristics = []
        
        if segment_data['ev_penetration_rate'].mean() > 0.06:
            characteristics.append('High EV Adoption')
        elif segment_data['ev_penetration_rate'].mean() > 0.03:
            characteristics.append('Moderate EV Adoption')
        else:
            characteristics.append('Low EV Adoption')
        
        if segment_data['gdp_per_capita'].mean() > 60000:
            characteristics.append('High Income')
        elif segment_data['gdp_per_capita'].mean() > 45000:
            characteristics.append('Middle Income')
        else:
            characteristics.append('Lower Income')
        
        if segment_data['total_stations'].mean() > 500:
            characteristics.append('Strong Infrastructure')
        elif segment_data['total_stations'].mean() > 200:
            characteristics.append('Moderate Infrastructure')
        else:
            characteristics.append('Limited Infrastructure')
        
        return characteristics

if __name__ == "__main__":
    # Example usage
    print("EV Intelligence Analytics - Machine Learning Models")
    print("This module provides forecasting and market segmentation capabilities.")
