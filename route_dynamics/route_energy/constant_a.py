import numpy as np

def const_a_dynamics(route_df, a_m, v_lim):
    # This section is the second (and more realistic) attempt
    # at modeling the bus speed along the route, by setting the
    # instantaneous bus acceleration and velocity to;
    #     a = v = 0 : at bus stops
    # accelerating away from bus stops at the constant rate
    #     a = a_m : away from bus stos
    # until the bus reaches the speed limit
    #     v = v_lim : constant speed limit of bus between stops
    # The bus decelerates at the same rate
    #     a = -a_m : decelleration approaching stops.
    #
    # Given the coordinate dataframe, we can assign velocity
    # and acceleration based on the distance of each point to
    # the next bus stop
    #     x = x_ns : array of distances from each route point
    #                to the next bus stop.
    # and the distance since the last bus stop
    #     x = x_ls : array of distances from each route point
    #                to the last bus stop.
    #
    # To assign the velocity and acceleration of each route
    # point, the distances 'x_ns' and 'x_ls' can be compared to
    # the distance required for the bus to accelerate to the
    # speed limit (as well as decelerate to v=0), 'x_a'. This
    # can be derived by considering the dynamical equations
    #     a = a_m
    #     v = a_m t + v_0
    #     x = 1/2 a_m t^2 + v_0 t + x_0
    # Considering acceleration away from a stop at 'x_0 = 0',
    #     x = 1/2 a_m t^2
    # and if 'x = x_a'  is the distance required to reach
    # 'v = v_lim', then the time required is given by
    #     v_lim = a_m t_lim
    #     -> t_lim = v_lim/a_m
    # and
    #     x_a = 1/2 a_m (v_lim/a_m)^2
    #         = v_lim^2 / (2 a_m)
    #
    # For route coordinates where 'x_ls < x_a', the speed will
    # be less than the speed limit. To calculate this speed,
    # consider the time required to accelerate to the point
    # 'x_1; x_ls < x_a',
    #     x_1 = 1/2 a_m t_1^2
    #     -> t_1 = sqrt(2 x_1 / a_m)
    # therefore the speed at point 'x_1' is
    #     v_1 = a_m t_1
    #         = a_m sqrt(2 x_1 / a_m)
    #         = sqrt(2 x_1 a_m)

    # Calculate distances to next and last bus stop.
    x_ns = np.zeros(len(route_df.index))
    x_ls = np.zeros(len(route_df.index))

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
                x_ns[i] += 1.8288
                if route_df.at[j, 'is_stop']:
                    break # done calulating 'x_ns' at this point
                # elif not bus stop: move to nest point, add distance

            # Calculate 'x_ls';
            # Iterate through previous indicies to cout distance to
            # last stop.
            for j in range(i, 0, -1):
                # Inclusive start to range because distances are
                # backward difference. Dont need to include 'j=0'
                # because the first point has no backward difference.
                if route_df.at[j, 'is_stop']:
                    break # done calulating x_ls at this point
                x_ls[i] += 1.8288


    # Define cutoff distance for acceleration and deceleration
    x_a = v_lim**2. / (2*a_m)

    x = (route_df.length.values)*0.3048 
    v = np.zeros(len(route_df.index))
    a = np.zeros(len(route_df.index))

    t = np.zeros(len(route_df.index))

    for i in range(len(x_ns)):
        # If close to last bus stop but far from next
        if (
            x_ls[i] <= x_a
            and
            x_ns[i] > x_a
            and
            not route_df.at[i, 'is_stop']
            ):

            a[i] = a_m
            v[i] = np.sqrt(2*x_ls[i]*a_m)

            if i > 0:
                # add time to clock
                t[i] += t[i-1]

                delta_t = np.sqrt(2/a_m)*(
                    np.sqrt(x_ls[i]) - np.sqrt(x_ls[i-1])
                    )
                t[i] += delta_t


        # or if close to next stop and far from last
        elif (
            x_ls[i] > x_a
            and
            x_ns[i] <= x_a
            and
            not route_df.at[i, 'is_stop']
            ):

            a[i] = -a_m
            v[i] = np.sqrt(2*x_ns[i]*a_m)

            # add time to clock
            t[i] += t[i-1]

            delta_t = np.sqrt(2/a_m)*(
                - np.sqrt(x_ns[i]) + np.sqrt(x_ns[i-1])
                )
            t[i] += delta_t

        # or far from both last and next stop, go speed limit
        elif (
            x_ls[i] > x_a
            and
            x_ns[i] > x_a
            and
            not route_df.at[i, 'is_stop']
            ):
            a[i] = 0
            v[i] = v_lim

            # add time to clock
            t[i] += t[i-1]

            delta_t = (x_ls[i] - x_ls[i-1])/v_lim
            t[i] += delta_t

        # But if too close to both last and next bus stops,
        elif (
            x_ls[i] <= x_a
            and
            x_ns[i] <= x_a
            and
            not route_df.at[i, 'is_stop']
            ):

            # add time to clock
            t[i] += t[i-1]

            if x_ls[i] < x_ns[i]:

                a[i] = a_m
                v[i] = np.sqrt(2*x_ls[i]*a_m)

                delta_t = np.sqrt(2/a_m)*(
                    np.sqrt(x_ls[i]) - np.sqrt(x_ls[i-1])
                    )

            elif x_ls[i] >= x_ns[i]:

                a[i] = -a_m
                v[i] = np.sqrt(2*x_ns[i]*a_m)

                delta_t = np.sqrt(2/a_m)*(
                    - np.sqrt(x_ns[i]) + np.sqrt(x_ns[i-1])
                    )

            # tick tock
            t[i] += delta_t

        elif route_df.at[i, 'is_stop']:
            # still want to progress time as if decellerating
            t[i] += t[i-1]

            delta_t = np.sqrt(2/a_m)*(
                - np.sqrt(x_ns[i]) + np.sqrt(x_ns[i-1])
                )
            t[i] += delta_t

    return a, v, x_ls, x_ns, t




