"""
FIT Converter Module
Converts Peloton workout data to Garmin FIT format
"""

from datetime import datetime, timedelta
import struct


class PelotonToFitConverter:
    """Convert Peloton workouts to FIT files"""
    
    def __init__(self, peloton_auth):
        """
        Initialize converter
        
        Args:
            peloton_auth: PelotonAuthenticator instance
        """
        self.peloton_auth = peloton_auth
    
    def convert_workout_to_fit(self, workout, output_path):
        """
        Convert a Peloton workout to FIT format
        
        Args:
            workout: Workout dictionary from Peloton API
            output_path: Path to save the FIT file
        """
        # Debug: Print workout structure
        print(f"\n=== Workout Data ===")
        print(f"ID: {workout.get('id')}")
        print(f"Created: {workout.get('created_at')}")
        print(f"Start time: {workout.get('start_time')}")
        print(f"End time: {workout.get('end_time')}")
        print(f"Total work: {workout.get('total_work')} (joules)")
        print(f"Calories: {workout.get('calories')}")
        print(f"Total Calories: {workout.get('total_calories')}")
        
        ride = workout.get('ride', {})
        print(f"Ride title: {ride.get('title')}")
        print(f"Ride duration: {ride.get('duration')}")
        print(f"Ride discipline: {ride.get('fitness_discipline')}")
        
        # Check for other calorie fields
        if 'leaderboard_rank' in workout:
            print(f"Leaderboard data: {workout.get('leaderboard_rank')}")
        
        # Fetch performance graph data
        print(f"Fetching performance data...")
        perf_graph = None
        try:
            if self.peloton_auth:
                perf_graph = self.peloton_auth.get_workout_performance_graph(workout.get('id'))
                if perf_graph:
                    print(f"✓ Got performance data with {len(perf_graph.get('metrics', []))} metric types")
                    # Show summary data if available
                    if 'summaries' in perf_graph:
                        print(f"Performance summaries: {perf_graph.get('summaries')}")
                else:
                    print("⚠ No performance data available")
        except Exception as e:
            print(f"⚠ Could not fetch performance data: {e}")
        
        print(f"===================\n")
        
        # Create FIT file with performance data
        try:
            self._create_fit_with_records(workout, perf_graph, output_path)
        except Exception as e:
            print(f"FIT creation error: {str(e)}")
            import traceback
            print(traceback.format_exc())
            raise
    
    def _create_fit_with_sdk(self, workout, output_path):
        """Create FIT file using Garmin FIT SDK"""
        try:
            from garmin_fit_sdk import Fit, Stream, Encoder
            from datetime import timezone
            
            # Create encoder
            fit = Fit()
            encoder = Encoder()
            
            # Get workout details
            ride = workout.get('ride', {})
            start_time = datetime.fromtimestamp(workout.get('created_at', 0))
            duration = ride.get('duration', 0)
            
            # File ID message
            file_id_msg = fit.file_id_mesg()
            file_id_msg.type = fit.file.value
            file_id_msg.manufacturer = 1  # Garmin
            file_id_msg.product = 0
            file_id_msg.time_created = int(start_time.timestamp() * 1000)
            
            encoder.write(file_id_msg)
            
            # Session message
            session_msg = fit.session_mesg()
            session_msg.timestamp = int(start_time.timestamp() * 1000)
            session_msg.start_time = int(start_time.timestamp() * 1000)
            
            # Map Peloton workout type to Garmin sport
            workout_type = ride.get('fitness_discipline', '').lower()
            if 'cycling' in workout_type or 'bike' in workout_type:
                session_msg.sport = fit.sport_cycling.value
                session_msg.sub_sport = fit.sub_sport_indoor_cycling.value
            elif 'running' in workout_type:
                session_msg.sport = fit.sport_running.value
                session_msg.sub_sport = fit.sub_sport_treadmill.value
            else:
                session_msg.sport = fit.sport_fitness_equipment.value
            
            session_msg.total_elapsed_time = duration
            session_msg.total_timer_time = duration
            session_msg.total_calories = workout.get('total_work', 0) // 1000
            
            encoder.write(session_msg)
            
            # Get performance data
            perf_data = self.peloton_auth.get_workout_performance_graph(workout.get('id'))
            
            if perf_data:
                self._add_performance_records(encoder, fit, start_time, perf_data)
            
            # Write to file
            with open(output_path, 'wb') as f:
                encoder.finish()
                f.write(encoder.bytes)
            
        except Exception as e:
            # Fallback to manual creation
            print(f"SDK creation failed: {e}, using manual method")
            self._create_fit_manually(workout, output_path)
    
    def _create_fit_with_records(self, workout, perf_graph, output_path):
        """
        Create FIT file with detailed record messages from performance data
        """
        # Get workout data
        ride = workout.get('ride', {})
        
        # Handle timestamp
        created_at = workout.get('created_at', 0)
        if created_at and created_at > 0:
            start_time = datetime.fromtimestamp(created_at)
        else:
            start_time = datetime.now()
        
        # Calculate duration
        start_ts = workout.get('start_time', 0)
        end_ts = workout.get('end_time', 0)
        
        if start_ts and end_ts:
            duration = int(end_ts - start_ts)
        elif ride.get('duration'):
            duration = int(ride.get('duration'))
        else:
            duration = 1800
        
        if duration < 1:
            duration = 60
        
        # Get calories - comprehensive search through all possible fields
        calories = 0
        calories_source = "none"
        
        print(f"\n=== Calorie Detection Debug ===")
        print(f"workout.get('calories'): {workout.get('calories')}")
        print(f"workout.get('total_calories'): {workout.get('total_calories')}")
        print(f"workout.get('calories_total'): {workout.get('calories_total')}")
        print(f"workout.get('total_work'): {workout.get('total_work')}")
        
        # Check performance graph for calorie summary
        if perf_graph and 'summaries' in perf_graph:
            print(f"Performance graph summaries: {perf_graph['summaries']}")
            for summary in perf_graph['summaries']:
                if summary.get('slug') == 'calories':
                    calories = int(summary.get('value', 0))
                    calories_source = "perf_graph.summaries.calories"
                    print(f"Found calories in perf_graph summaries: {calories}")
                    break
        
        # Priority order for finding calories
        if not calories and 'calories' in workout and workout['calories']:
            calories = int(workout['calories'])
            calories_source = "workout.calories"
        elif not calories and 'total_calories' in workout and workout['total_calories']:
            calories = int(workout['total_calories'])
            calories_source = "workout.total_calories"
        elif not calories and 'calories_total' in workout and workout['calories_total']:
            calories = int(workout['calories_total'])
            calories_source = "workout.calories_total"
        
        # If still no calories, estimate from work
        if not calories:
            total_work_j = workout.get('total_work', 0)
            if isinstance(total_work_j, (int, float)) and total_work_j > 0:
                # Peloton total_work is in joules
                # Mechanical efficiency is ~20-25%, so multiply by 4
                calories = int((total_work_j / 4184) * 4)
                calories_source = f"estimated from {total_work_j}J work"
        
        if calories < 0:
            calories = 0
        
        print(f"Final calories: {calories} kcal (from: {calories_source})")
        print(f"===============================\n")
        
        # Determine sport type
        workout_title = ride.get('title', '').lower()
        discipline = ride.get('fitness_discipline', '').lower() if ride.get('fitness_discipline') else ''
        
        sport = 2  # Default to cycling
        
        if discipline:
            if 'running' in discipline or 'run' in discipline:
                sport = 1
            elif 'cycling' in discipline or 'bike' in discipline or 'cycle' in discipline:
                sport = 2
            elif 'strength' in discipline or 'bootcamp' in discipline:
                sport = 4
        elif workout_title:
            if 'run' in workout_title or 'tread' in workout_title:
                sport = 1
            elif 'ride' in workout_title or 'bike' in workout_title or 'cycling' in workout_title:
                sport = 2
            elif 'strength' in workout_title or 'bootcamp' in workout_title:
                sport = 4
        
        # Parse performance data
        metrics_data = {}
        if perf_graph and 'metrics' in perf_graph:
            for metric in perf_graph['metrics']:
                slug = metric.get('slug', '')
                values = metric.get('values', [])
                if values:
                    metrics_data[slug] = values
                    print(f"Found {len(values)} data points for {slug}")
        
        # FIT file structure
        fit_data = bytearray()
        messages = bytearray()
        
        # File ID message
        file_id = self._create_file_id_message(start_time)
        messages.extend(file_id)
        
        # Add record messages with detailed data and track distance
        self._calculated_distance = 0
        if metrics_data:
            print(f"Creating record messages with performance data...")
            record_msgs = self._create_record_messages_with_distance(start_time, metrics_data, sport)
            messages.extend(record_msgs)
        else:
            print(f"No performance data, creating basic session...")
        
        # Session message (now includes distance if calculated)
        session = self._create_session_message(workout, start_time, duration, calories, sport)
        messages.extend(session)
        
        # Activity message
        activity = self._create_activity_message(start_time, duration)
        messages.extend(activity)
        
        # Build header
        data_size = len(messages)
        fit_data.append(14)  # header size
        fit_data.append(0x20)  # protocol version
        fit_data.extend(struct.pack('<H', 2132))  # profile version
        fit_data.extend(struct.pack('<I', data_size))
        fit_data.extend(b'.FIT')
        fit_data.extend(struct.pack('<H', 0))  # header CRC
        
        # Add messages
        fit_data.extend(messages)
        
        # Calculate and add file CRC
        crc = self._calculate_crc(fit_data)
        fit_data.extend(struct.pack('<H', crc))
        
        # Write to file
        with open(output_path, 'wb') as f:
            f.write(fit_data)
        
        print(f"FIT file created: {len(fit_data)} bytes with {calories} calories")
    
    def _create_record_messages_with_distance(self, start_time, metrics_data, sport):
        """Create record messages and track total distance"""
        # Create messages
        messages = self._create_record_messages(start_time, metrics_data, sport)
        
        # Calculate total distance from speed data
        if 'speed' in metrics_data:
            total_distance_m = 0
            for spd in metrics_data['speed']:
                if spd is not None and spd > 0:
                    # Speed in mph, convert to m/s, multiply by 1 second
                    total_distance_m += (spd * 0.44704)
            
            self._calculated_distance = total_distance_m
        
        return messages
    
    def _create_record_messages(self, start_time, metrics_data, sport):
        """Create record messages with per-second data"""
        messages = bytearray()
        
        # Map Peloton metric names to what we need
        # Peloton metrics: heart_rate, output (watts), cadence, resistance, speed
        has_heart_rate = 'heart_rate' in metrics_data
        has_cadence = 'cadence' in metrics_data
        has_power = 'output' in metrics_data
        has_speed = 'speed' in metrics_data
        has_resistance = 'resistance' in metrics_data
        
        # Get the length of data (all metrics should have same length)
        data_length = 0
        for metric_name in ['heart_rate', 'cadence', 'output', 'speed']:
            if metric_name in metrics_data:
                data_length = len(metrics_data[metric_name])
                break
        
        if data_length == 0:
            print("⚠ No metric data found")
            return messages
        
        print(f"Creating {data_length} record messages")
        print(f"Available metrics: {list(metrics_data.keys())}")
        
        # DEBUG: Show sample speed values to determine units
        if has_speed:
            speed_samples = [s for s in metrics_data['speed'][:20] if s is not None]
            if speed_samples:
                avg_speed = sum(speed_samples) / len(speed_samples)
                max_speed = max(speed_samples)
                print(f"Speed samples (first 20): min={min(speed_samples):.2f}, avg={avg_speed:.2f}, max={max_speed:.2f}")
                print(f"If these are mph, avg={avg_speed:.1f} mph (seems {'reasonable' if 5 < avg_speed < 30 else 'WRONG - might be kph or m/s'})")
        
        # Create record definition message
        record_def = bytearray()
        record_def.append(0x40)  # Definition message, local message 0
        record_def.append(0x00)  # Reserved
        record_def.append(0x00)  # Little endian
        record_def.extend(struct.pack('<H', 20))  # Global message number (record)
        
        # Count fields
        field_count = 1  # timestamp always included
        if has_heart_rate:
            field_count += 1
        if has_cadence:
            field_count += 1
        if has_power:
            field_count += 1
        if has_speed:
            field_count += 1
        
        record_def.append(field_count)
        
        # Field 0: timestamp (required)
        record_def.append(253)  # field number
        record_def.append(4)    # size
        record_def.append(0x86) # uint32
        
        # Add optional fields
        if has_heart_rate:
            record_def.append(3)    # heart_rate field
            record_def.append(1)    # size
            record_def.append(0x02) # uint8
        
        if has_cadence:
            record_def.append(4)    # cadence field
            record_def.append(1)    # size
            record_def.append(0x02) # uint8
        
        if has_power:
            record_def.append(7)    # power field
            record_def.append(2)    # size
            record_def.append(0x84) # uint16
        
        if has_speed:
            record_def.append(5)    # speed field (m/s * 1000)
            record_def.append(2)    # size
            record_def.append(0x84) # uint16
        
        messages.extend(record_def)
        
        # Create data messages
        fit_epoch = datetime(1989, 12, 31, 0, 0, 0)
        
        # Track cumulative distance for validation
        total_distance_m = 0
        valid_records = 0
        
        for i in range(data_length):
            # Check if we have any valid data for this second
            has_data = False
            if has_heart_rate and metrics_data['heart_rate'][i] is not None:
                has_data = True
            if has_cadence and metrics_data['cadence'][i] is not None:
                has_data = True
            if has_power and metrics_data['output'][i] is not None:
                has_data = True
            if has_speed and metrics_data['speed'][i] is not None:
                has_data = True
            
            if not has_data:
                continue
            
            record_data = bytearray()
            record_data.append(0x00)  # Data message, local message 0
            
            # Timestamp
            record_time = start_time + timedelta(seconds=i)
            fit_time = int((record_time - fit_epoch).total_seconds())
            fit_time = max(0, min(fit_time, 0xFFFFFFFF))
            record_data.extend(struct.pack('<I', fit_time))
            
            # Heart rate
            if has_heart_rate:
                hr = metrics_data['heart_rate'][i]
                if hr is not None and hr > 0:
                    record_data.append(min(int(hr), 255))
                else:
                    record_data.append(0xFF)  # Invalid value
            
            # Cadence
            if has_cadence:
                cad = metrics_data['cadence'][i]
                if cad is not None and cad > 0:
                    record_data.append(min(int(cad), 255))
                else:
                    record_data.append(0xFF)  # Invalid value
            
            # Power
            if has_power:
                pwr = metrics_data['output'][i]
                if pwr is not None and pwr > 0:
                    record_data.extend(struct.pack('<H', min(int(pwr), 65535)))
                else:
                    record_data.extend(struct.pack('<H', 0xFFFF))  # Invalid value
            
            # Speed - CHECK IF UNITS ARE CORRECT
            if has_speed:
                spd = metrics_data['speed'][i]
                if spd is not None and spd > 0:
                    # HYPOTHESIS: Peloton speed might be in kph, not mph
                    # Test: If avg speed in data is ~17 (kph) vs ~10.5 (mph)
                    # FIT needs m/s * 1000
                    
                    # Assume Peloton gives mph (US company)
                    # 1 mph = 0.44704 m/s
                    speed_ms_1000 = int(spd * 0.44704 * 1000)
                    record_data.extend(struct.pack('<H', min(speed_ms_1000, 65535)))
                    
                    # Track distance (speed in m/s * 1 second = meters)
                    total_distance_m += (spd * 0.44704)
                else:
                    record_data.extend(struct.pack('<H', 0xFFFF))  # Invalid value
            
            messages.extend(record_data)
            valid_records += 1
        
        print(f"✓ Created {valid_records} valid record messages")
        print(f"✓ Metrics included: HR={has_heart_rate}, Cadence={has_cadence}, Power={has_power}, Speed={has_speed}")
        if has_speed:
            total_distance_mi = total_distance_m / 1609.34
            print(f"✓ Calculated distance from speed: {total_distance_mi:.2f} mi ({total_distance_m:.0f} m)")
        
        return messages
    
    def _create_fit_manually(self, workout, output_path):
        """
        Create FIT file manually (fallback method)
        Creates a minimal but valid FIT file
        """
        # Get workout data with safe defaults
        ride = workout.get('ride', {})
        
        # Handle timestamp - ensure it's valid
        created_at = workout.get('created_at', 0)
        if created_at and created_at > 0:
            start_time = datetime.fromtimestamp(created_at)
        else:
            start_time = datetime.now()
        
        # Calculate duration from start_time and end_time
        start_ts = workout.get('start_time', 0)
        end_ts = workout.get('end_time', 0)
        
        if start_ts and end_ts:
            # Use actual workout duration
            duration = int(end_ts - start_ts)
        elif ride.get('duration'):
            # Fallback to ride duration
            duration = int(ride.get('duration'))
        else:
            # Last resort: default
            duration = 1800
        
        # Ensure minimum duration
        if duration < 1:
            duration = 60
        
        # Handle calories - ensure it's an integer
        total_work = workout.get('total_work', 0)
        if isinstance(total_work, (int, float)):
            # Peloton total_work is in joules, convert to kcal
            # 1 kcal = 4184 joules
            calories = int(total_work / 4184) if total_work > 0 else 0
        else:
            calories = 0
        
        # Ensure minimum values
        if calories < 0:
            calories = 0
        
        # Determine sport type - default to cycling since this is Peloton
        # Peloton workouts without fitness_discipline are usually cycling
        workout_title = ride.get('title', '').lower()
        discipline = ride.get('fitness_discipline', '').lower() if ride.get('fitness_discipline') else ''
        
        # Default to cycling for Peloton (most common)
        sport = 2  # cycling
        sub_sport = 6  # indoor_cycling
        
        # Check discipline field first
        if discipline:
            if 'running' in discipline or 'run' in discipline:
                sport = 1  # running
                sub_sport = 1  # treadmill
            elif 'cycling' in discipline or 'bike' in discipline or 'cycle' in discipline:
                sport = 2  # cycling
                sub_sport = 6  # indoor_cycling
            elif 'strength' in discipline or 'bootcamp' in discipline:
                sport = 4  # fitness_equipment
                sub_sport = 0  # generic
        # If no discipline, check title
        elif workout_title:
            if 'run' in workout_title or 'tread' in workout_title:
                sport = 1  # running
                sub_sport = 1  # treadmill
            elif 'ride' in workout_title or 'bike' in workout_title or 'cycling' in workout_title:
                sport = 2  # cycling
                sub_sport = 6  # indoor_cycling
            elif 'strength' in workout_title or 'bootcamp' in workout_title:
                sport = 4  # fitness_equipment
                sub_sport = 0  # generic
        
        print(f"Sport determined: {sport} (2=cycling, 1=running, 4=fitness)")
        print(f"Duration: {duration} seconds ({duration/60:.1f} minutes)")
        print(f"Calories: {calories} kcal (from {total_work} joules)")
        
        # FIT file structure
        fit_data = bytearray()
        
        # FIT header (14 bytes)
        header_size = 14
        protocol_version = 0x20  # 2.0
        profile_version = 2132  # 21.32
        data_size = 0  # Will calculate later
        data_type = b'.FIT'
        
        # We'll build the data first, then add header
        messages = bytearray()
        
        # File ID message (required)
        file_id = self._create_file_id_message(start_time)
        messages.extend(file_id)
        
        # Session message
        session = self._create_session_message(workout, start_time, duration, calories, sport)
        messages.extend(session)
        
        # Activity message
        activity = self._create_activity_message(start_time, duration)
        messages.extend(activity)
        
        # Calculate CRC
        data_size = len(messages)
        
        # Build header
        fit_data.append(header_size)
        fit_data.append(protocol_version)
        fit_data.extend(struct.pack('<H', profile_version))
        fit_data.extend(struct.pack('<I', data_size))
        fit_data.extend(data_type)
        
        # CRC of header (optional, set to 0)
        fit_data.extend(struct.pack('<H', 0))
        
        # Add messages
        fit_data.extend(messages)
        
        # Calculate and add CRC of entire file
        crc = self._calculate_crc(fit_data)
        fit_data.extend(struct.pack('<H', crc))
        
        # Write to file
        with open(output_path, 'wb') as f:
            f.write(fit_data)
    
    def _create_file_id_message(self, timestamp):
        """Create FIT file ID message"""
        msg = bytearray()
        
        # Definition message for file_id (global message 0)
        msg.append(0x40)  # Definition message, local message 0
        msg.append(0x00)  # Reserved
        msg.append(0x00)  # Architecture (little endian)
        msg.extend(struct.pack('<H', 0))  # Global message number (file_id)
        msg.append(4)  # Number of fields
        
        # Field definitions
        msg.append(0)  # type
        msg.append(1)  # size
        msg.append(0)  # base type (enum)
        
        msg.append(1)  # manufacturer
        msg.append(2)  # size
        msg.append(0x84)  # base type (uint16)
        
        msg.append(2)  # product
        msg.append(2)  # size
        msg.append(0x84)  # base type (uint16)
        
        msg.append(4)  # time_created
        msg.append(4)  # size
        msg.append(0x86)  # base type (uint32)
        
        # Data message
        msg.append(0x00)  # Data message, local message 0
        msg.append(4)  # type = activity
        msg.extend(struct.pack('<H', 1))  # manufacturer = garmin
        msg.extend(struct.pack('<H', 0))  # product
        
        # Convert timestamp to FIT time (seconds since Dec 31, 1989 UTC)
        fit_epoch = datetime(1989, 12, 31, 0, 0, 0)
        fit_time = int((timestamp - fit_epoch).total_seconds())
        # Ensure it's a valid unsigned 32-bit integer
        fit_time = max(0, min(fit_time, 0xFFFFFFFF))
        msg.extend(struct.pack('<I', fit_time))
        
        return msg
    
    def _create_session_message(self, workout, start_time, duration, calories, sport=2):
        """Create FIT session message with distance"""
        msg = bytearray()
        
        # Ensure all values are valid integers
        duration = int(duration)
        calories = int(calories)
        sport = int(sport)
        
        # Calculate distance from speed data if available
        distance_m = 0
        if hasattr(self, '_calculated_distance'):
            distance_m = self._calculated_distance
        
        # Definition message for session (global message 18)
        msg.append(0x41)  # Definition message, local message 1
        msg.append(0x00)  # Reserved
        msg.append(0x00)  # Architecture (little endian)
        msg.extend(struct.pack('<H', 18))  # Global message number (session)
        
        # Include distance field if we have it
        field_count = 6 if distance_m > 0 else 5
        msg.append(field_count)
        
        # Field definitions
        msg.append(253)  # timestamp
        msg.append(4)
        msg.append(0x86)
        
        msg.append(2)  # start_time
        msg.append(4)
        msg.append(0x86)
        
        msg.append(7)  # total_elapsed_time
        msg.append(4)
        msg.append(0x86)
        
        msg.append(5)  # sport
        msg.append(1)
        msg.append(0)
        
        msg.append(11)  # total_calories
        msg.append(2)
        msg.append(0x84)
        
        if distance_m > 0:
            msg.append(9)   # total_distance (cm)
            msg.append(4)
            msg.append(0x86)
        
        # Data message
        msg.append(0x01)  # Data message, local message 1
        
        fit_epoch = datetime(1989, 12, 31, 0, 0, 0)
        fit_time = int((start_time - fit_epoch).total_seconds())
        fit_time = max(0, min(fit_time, 0xFFFFFFFF))
        
        msg.extend(struct.pack('<I', fit_time))  # timestamp
        msg.extend(struct.pack('<I', fit_time))  # start_time
        
        # Duration in milliseconds
        duration_ms = duration * 1000
        duration_ms = max(0, min(duration_ms, 0xFFFFFFFF))
        msg.extend(struct.pack('<I', duration_ms))
        
        msg.append(sport)  # sport (2=cycling, 1=running, 4=fitness)
        
        # Calories must fit in uint16
        calories = max(0, min(calories, 65535))
        msg.extend(struct.pack('<H', calories))
        
        # Distance in centimeters (m * 100)
        if distance_m > 0:
            distance_cm = int(distance_m * 100)
            distance_cm = max(0, min(distance_cm, 0xFFFFFFFF))
            msg.extend(struct.pack('<I', distance_cm))
            print(f"Session distance: {distance_m:.0f}m ({distance_m/1609.34:.2f} mi)")
        
        return msg
    
    def _create_activity_message(self, timestamp, duration):
        """Create FIT activity message"""
        msg = bytearray()
        
        # Ensure duration is valid
        duration = int(duration) if duration else 60
        
        # Definition message for activity (global message 34)
        msg.append(0x42)  # Definition message, local message 2
        msg.append(0x00)
        msg.append(0x00)
        msg.extend(struct.pack('<H', 34))  # Global message number (activity)
        msg.append(3)  # Number of fields
        
        msg.append(253)  # timestamp
        msg.append(4)
        msg.append(0x86)
        
        msg.append(1)  # num_sessions
        msg.append(2)
        msg.append(0x84)
        
        msg.append(2)  # type
        msg.append(1)
        msg.append(0)
        
        # Data message
        msg.append(0x02)  # Data message, local message 2
        
        fit_epoch = datetime(1989, 12, 31, 0, 0, 0)
        fit_time = int((timestamp - fit_epoch).total_seconds())
        fit_time = max(0, min(fit_time, 0xFFFFFFFF))
        
        msg.extend(struct.pack('<I', fit_time))
        msg.extend(struct.pack('<H', 1))  # num_sessions
        msg.append(0)  # type = manual
        
        return msg
    
    def _calculate_crc(self, data):
        """Calculate CRC-16 for FIT file"""
        crc = 0
        for byte in data:
            for _ in range(8):
                if (crc & 0x1) != (byte & 0x1):
                    crc = ((crc >> 1) & 0x7FFF) ^ 0xA001
                else:
                    crc = (crc >> 1) & 0x7FFF
                byte >>= 1
        return crc
    
    def _add_performance_records(self, encoder, fit, start_time, perf_data):
        """Add performance record messages"""
        # Extract metrics from performance data
        metrics = perf_data.get('metrics', [])
        
        for metric in metrics:
            if metric.get('slug') == 'heart_rate':
                values = metric.get('values', [])
                for i, value in enumerate(values):
                    if value is not None:
                        timestamp = start_time + timedelta(seconds=i)
                        
                        record_msg = fit.record_mesg()
                        record_msg.timestamp = int(timestamp.timestamp() * 1000)
                        record_msg.heart_rate = int(value)
                        
                        encoder.write(record_msg)


if __name__ == "__main__":
    print("FIT Converter Module")
    print("=" * 60)
    print("\nThis module converts Peloton workouts to Garmin FIT format.")
    print("Use it through the main application.")