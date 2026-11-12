(Resources-test-plan)=
# Resources test plan

:::{note}
`resources` has been part of `main` since Ubuntu 26.04 LTS (resolute).
:::

Below are the test cases that should be run when **`resources`** is updated to new minor releases in the development version of Ubuntu. These should also be run for any Stable Release Update for **`resources`**.


## Test case "Main"

1. Open Resources
2. Verify that the sidebar lists devices:
   * CPU
   * Memory
   * GPU
   * Physical storage
   * Physical network
   * Battery (if any)


## Test case "Virtual"

1. Navigate to Preferences > Devices
2. Enable "Show Virtual Drives"
3. Verify that any loop devices are listed in the sidebar
4. Enable "Show Virtual Network Interfaces"
5. Verify that any virtual network interfaces are listed in the sidebar


## Test case "Apps"

1. Navigate to "Apps"
2. Verify that the main view lists open graphical applications (including those running in the background, without any visible window)
3. Click on "Processor"
4. Verify that the list is sorted by CPU usage
5. Select an application
6. Click on "End App"
7. Verify that the app was closed


## Test case "Processes"

1. Navigate to "Processes"
2. Verify that the main view lists processes running for any user
3. Verify that processes associated with a graphical application are shown their icon
4. Click on "Memory"
5. Verify that the list is sorted by memory usage
6. Start typing
7. Verify that the list is filtered by the search query
8. Select a process
9. Click on the info button
10. Verify that a dialog appears with detailed usage and properties information


## Test case "Memory"

1. Navigate to "Memory"
2. Verify that usage graphs are visible for:
   * Physical memory
   * Swap memory
3. Verify that information on the memory total capacity is shown
4. Verify that information on the memory speed is shown


## Test case "Processor"

1. Navigate to "Processor"
2. Verify that graphs are visible for:
   * CPU usage
   * CPU temperature
3. Verify that information on the physical core count is shown
4. Verify that information on the logical core count is shown
5. Verify that information on the max CPU clock frequency is shown
6. Select "Show Usages of Logical CPUs"
7. Verify that usage graphs are visible for each individual logical CPU core


## Test case "GPU"

1. Navigate to "GPU"
2. Verify that graphs are visible for:
   * Total usage
   * Video Memory Usage
   * Video Encoder Usage (if supported)
   * Video Decoder Usage (if supported)
   * Temperature (if supported)
3. Verify that information on the max GPU clock frequency is shown (if supported)
4. Verify that information on the GPU power draw is shown (if supported)


## Test case "Storage"

1. Click on one of the physical storage drives in the sidebar
2. Verify that graphs are visible for:
   * Drive activity
   * Read speed
   * Write speed
3. Verify that information on the drive's capacity is shown


## Test case "Network"

1. Click on one of the physical network cards in the sidebar (e.g. Wi-Fi Connection)
2. Verify that graphs are visible for:
   * _Receiving_ speed
   * _Sending_ speed
3. Verify that the network's hardware address is shown
4. If Wi-Fi, verify that the Wi-Fi network name is shown
5. If Wi-Fi, verify that information on the Wi-Fi technology is shown (e.g. Wi-Fi 6)


## Test case "Battery"

1. Skip this test if the machine does not have a battery
2. Click on the battery in the sidebar
3. Verify that graphs are visible for:
   * Charge level
   * Power draw
4. Verify that information on the battery capacity is shown
5. Verify that information on the battery health is shown
