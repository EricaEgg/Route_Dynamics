import pandas as pd
import numpy as np

def accel_dynamics(route_df, a_prof, a_pos, a_neg):

    data = a_prof

    #rounding values
    data['time (s)'] = data['time (s)'].round(0)
    data['accel. (g)'] = data['accel. (g)'].round(4)

    #Convert to SI units
    data['accel. (m/s^2)'] = data['accel. (g)']*9.81

    #Calculate Velocity

    data['vel. (m/s)'] = np.zeros(len(data.index))

    for i in range(1, len(data)):
        data['vel. (m/s)'][i] = ((data['accel. (m/s^2)'][i] + data['accel. (m/s^2)'][i-1])/2*1) + data['vel. (m/s)'][i-1]
    
    data['vel. (mph)'] = data['vel. (m/s)']*2.2

    #Calculate Distance

    data['dist. (m)'] = np.zeros(len(data.index))

    for i in range(1, len(data)):
        data['dist. (m)'][i] = ((data['vel. (m/s)'][i] + data['vel. (m/s)'][i-1])/2*1) + data['dist. (m)'][i-1]

    
    data['dist.(km)'] = data['dist. (m)']/1000
    data['dist. (ft)'] = data['dist. (m)']*3.28

    #Create new dataframe where dist. is the indep var

    data2 = pd.DataFrame({'dist. (ft)': np.arange(0, 1260, 36)})
    data2['dist. (m)'] = data2['dist. (ft)']/3.281

    data2['vel. (m/s)'] = np.zeros(len(data2.index))

    data2['vel. (km/hr)'] = np.zeros(len(data2.index))

    data2['vel. (mph)'] = np.zeros(len(data2.index))

    data2['accel. (m/s^2)'] = np.zeros(len(data2.index))

    data2['time (s)'] = np.zeros(len(data2.index))

    for i in range(1, len(data2)):

        z = data2['dist. (ft)'].iloc[i]
        params = data.iloc[(data['dist. (ft)']-z).abs().argsort()[:1]]
        row = params.index.values


        #Interpolate
        if params['dist. (ft)'].values < z:
            vel = ((data['vel. (m/s)'][row+1].values - data['vel. (m/s)'][row].values)/(data['dist. (m)'][row +1].values - data['dist. (m)'][row].values) * (z/3.28 - data['dist. (m)'][row].values)) + data['vel. (m/s)'][row].values
            accel = ((data['accel. (m/s^2)'][row+1].values - data['accel. (m/s^2)'][row].values)/(data['dist. (m)'][row +1].values - data['dist. (m)'][row].values) * (z/3.28 - data['dist. (m)'][row].values)) + data['accel. (m/s^2)'][row].values
            time = ((data['time (s)'][row+1].values - data['time (s)'][row].values)/(data['dist. (m)'][row +1].values - data['dist. (m)'][row].values) * (z/3.28 - data['dist. (m)'][row].values)) + data['time (s)'][row].values
        else:
            vel = ((data['vel. (m/s)'][row].values - data['vel. (m/s)'][row-1].values)/(data['dist. (m)'][row].values - data['dist. (m)'][row-1].values) * (z/3.28 - data['dist. (m)'][row-1].values)) + data['vel. (m/s)'][row-1].values
            accel = ((data['accel. (m/s^2)'][row].values - data['accel. (m/s^2)'][row-1].values)/(data['dist. (m)'][row].values - data['dist. (m)'][row-1].values) * (z/3.28 - data['dist. (m)'][row-1].values)) + data['accel. (m/s^2)'][row-1].values
            time = ((data['time (s)'][row].values - data['time (s)'][row-1].values)/(data['dist. (m)'][row].values - data['dist. (m)'][row-1].values) * (z/3.28 - data['dist. (m)'][row-1].values)) + data['time (s)'][row-1].values
        
    
        data2['vel. (m/s)'].iloc[i] = vel
        data2['vel. (km/hr)'].iloc[i] = vel * 3.6
        data2['vel. (mph)'].iloc[i] = vel*2.2
        data2['accel. (m/s^2)'].iloc[i] = accel
        data2['time (s)'].iloc[i] = time

    # Distance of accel profile

    x_p = data2['dist. (m)'].iloc[-1]

    x_ns = np.zeros(len(route_df.index)) #next stops
    x_ls = np.zeros(len(route_df.index)) # prev. stops

    for i in range(len(x_ns)):
        # set values to Nan if bus stop
        if route_df.at[i, 'is_stop']:
            x_ns[i] = 0.
            x_ls[i] = 0.
            # move to next point
            continue
        else:
            # Calculate 'x_ns';
            # Iterate through remaining indicies to count distance to
            # next stop.
            for j in range(i+1, len(x_ns)):
                # add distance to next point to 'x_ns'
                x_ns[i] += 10.972265 
                if route_df.at[j, 'is_stop']:
                    break # done calulating 'x_ns' at this point
                # elif not bus stop: move to next point, add distance

            # Calculate 'x_ls';
            # Iterate through previous indicies to cout distance to
            # last stop.
            for j in range(i, 0, -1):
                # Inclusive start to range because distances are
                # backward difference. Dont need to include 'j=0'
                # because the first point has no backward difference.
                if route_df.at[j, 'is_stop']:
                    break # done calulating x_ls at this point
                x_ls[i] += 10.972265

    v = np.zeros(len(route_df.index)) #array for vel.
    a = np.zeros(len(route_df.index)) #array for accel.

    count = 0

    for i in range(len(x_ns)):
        x_d = route_df['speed_limit'].iloc[i]**2. / (2*a_neg)
        v_lim = route_df['speed_limit'].iloc[i]

        if count > i:
            continue

        else:

            #Case 1

            if (
                x_ns[i]<=abs(x_d)
                and
                not route_df.at[i, 'is_stop']
                ):

                a[i] = a_neg
                v[i] = np.sqrt(-2*x_ns[i]*a_neg)
                count += 1

            #Case 2

            elif (
                x_ns[i] > abs(x_d)
                and
                x_ls[i] >= x_p
                and
                not route_df.at[i, 'is_stop']
                ):

                if v[i-1] < v_lim:

                    a[i] = a_pos
                    v[i] = np.sqrt(2*x_ns[i]*a[i])
                    count += 1

                elif v[i-1]>v_lim:

                    while x_ns[count]>abs(x_d):

                        a[count] = 0
                        v[count] = v_lim

                        count+=1

                    else:
                        continue 

                else:
                    continue



            #Case 3

            elif (
                x_ls[i] < x_p
                and
                x_ns[i] > abs(x_d)
                and
                not route_df.at[i, 'is_stop']
                ):

                for j in range(len(data2)):

                    if count < len(x_ns):

                        if v[count-1] < v_lim:

                            while x_ns[count]>abs(x_d) and j<len(data2) and v[count-1] < v_lim:
                                a[count] = data2['accel. (m/s^2)'].iloc[j]
                                v[count] = data2['vel. (m/s)'].iloc[j]
                                j+=1
                                count+=1

                            else:
                                continue



                        elif v[count-1]>=v_lim:

                            while x_ns[count]>abs(x_d):

                                a[count] = 0
                                v[count] = v_lim

                                count+=1

                            else:
                                continue

                        else:
                            continue

                    else:
                        break


            elif route_df.at[i, 'is_stop']:

                count += 1

    back_diff_delta_x = np.full(len(route_df), 10.9728)


    segment_avg_velocities = (
                    v
                    +
                    np.append(0,v[:-1])
                    )/2

    delta_times = back_diff_delta_x / segment_avg_velocities
    delta_times[delta_times > 1000000] = 0

    for i in range(len(route_df)):
        if route_df.at[i, 'is_bus_stop']:
            delta_times[i]+=30 #make variable later

        elif route_df.at[i, 'is_signal']:
            delta_times[i]+=30 #make variable later
        else:
            pass

    #time_on_route = np.append(0, np.cumsum(delta_times[1:]))

    #t = time_on_route

    


    return a, v, x_ls, x_ns, delta_times
