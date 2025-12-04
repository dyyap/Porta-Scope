#include <stdio.h>
#include <errno.h>
#include <unistd.h>
#include <stdlib.h>
#include <string.h>
#include <signal.h>
#include <math.h>
#include <jack/jack.h>

#ifndef M_PI
#    define M_PI 3.14159265358979323846
#endif


typedef struct {
    jack_port_t *output_port;
    jack_client_t *client;
    float frequency;
    float sample_rate;
    float phase;
    int running;
} sine_data_t;

sine_data_t sine_data;

/**
 * The process callback for this JACK application is called in a
 * special realtime thread once for each audio cycle.
 */
int process(jack_nframes_t nframes, void *arg) {
    sine_data_t *data = (sine_data_t *) arg;
    jack_default_audio_sample_t *out;
    float phase_increment;
    unsigned int i;

    out = jack_port_get_buffer(data->output_port, nframes);
   
    // Calculate phase increment for each sample
    phase_increment = 2.0f * M_PI * data->frequency / data->sample_rate;
   
    // Generate sine wave samples
    for (i = 0; i < nframes; i++) {
        out[i] = 0.3f * sinf(data->phase); // 0.3 for volume control
        data->phase += phase_increment;
       
        // Keep phase in reasonable range to avoid precision issues
        if (data->phase >= 2.0f * M_PI) {
            data->phase -= 2.0f * M_PI;
        }
    }
   
    return 0;
}

/**
 * JACK calls this shutdown_callback if the server ever shuts down or
 * decides to disconnect the client.
 */
void jack_shutdown(void *arg) {
    sine_data_t *data = (sine_data_t *) arg;
    data->running = 0;
    fprintf(stderr, "JACK shut down, exiting...\n");
}

void signal_handler(int sig) {
    sine_data.running = 0;
    fprintf(stderr, "\nStopping...\n");
}

int main(int argc, char *argv[]) {
    const char **ports;
    const char *client_name = "sine_generator";
    const char *server_name = NULL;
    jack_options_t options = JackNullOption;
    jack_status_t status;
   
    // Initialize sine data
    sine_data.frequency = 440.0f; // A4 note
    sine_data.phase = 0.0f;
    sine_data.running = 1;
   
    // Parse command line arguments for frequency
    if (argc > 1) {
        sine_data.frequency = atof(argv[1]);
        if (sine_data.frequency <= 0) {
            fprintf(stderr, "Invalid frequency: %s\n", argv[1]);
            return 1;
        }
    }
   
    printf("Generating sine wave at %.2f Hz\n", sine_data.frequency);
   
    // Set up signal handlers
    signal(SIGINT, signal_handler);
    signal(SIGTERM, signal_handler);
   
    // Open a client connection to the JACK server
    sine_data.client = jack_client_open(client_name, options, &status, server_name);
    if (sine_data.client == NULL) {
        fprintf(stderr, "jack_client_open() failed, status = 0x%2.0x\n", status);
        if (status & JackServerFailed) {
            fprintf(stderr, "Unable to connect to JACK server\n");
        }
        return 1;
    }
   
    if (status & JackServerStarted) {
        fprintf(stderr, "JACK server started\n");
    }
   
    if (status & JackNameNotUnique) {
        client_name = jack_get_client_name(sine_data.client);
        fprintf(stderr, "unique name `%s' assigned\n", client_name);
    }
   
    // Get sample rate
    sine_data.sample_rate = jack_get_sample_rate(sine_data.client);
    printf("Sample rate: %.0f Hz\n", sine_data.sample_rate);
   
    // Tell the JACK server to call `process()` whenever there is work to be done
    jack_set_process_callback(sine_data.client, process, &sine_data);
   
    // Tell the JACK server to call `jack_shutdown()` if it ever shuts down
    jack_on_shutdown(sine_data.client, jack_shutdown, &sine_data);
   
    // Create output port
    sine_data.output_port = jack_port_register(sine_data.client, "output",
                                               JACK_DEFAULT_AUDIO_TYPE,
                                               JackPortIsOutput, 0);
   
    if (sine_data.output_port == NULL) {
        fprintf(stderr, "no more JACK ports available\n");
        return 1;
    }
   
    // Tell the JACK server that we are ready to roll
    if (jack_activate(sine_data.client)) {
        fprintf(stderr, "cannot activate client");
        return 1;
    }
   
    // Connect the port to the system playback ports
    ports = jack_get_ports(sine_data.client, NULL, NULL,
                          JackPortIsPhysical | JackPortIsInput);
    if (ports == NULL) {
        fprintf(stderr, "no physical playback ports\n");
        return 1;
    }
   
    // Connect to the first available playback port (usually left channel)
    if (jack_connect(sine_data.client, jack_port_name(sine_data.output_port), "audio_receiver:input")) {
        fprintf(stderr, "cannot connect output port\n");
    }
   
    // Optionally connect to stereo output (right channel)
    if (ports[1] != NULL) {
        if (jack_connect(sine_data.client, jack_port_name(sine_data.output_port), ports[1])) {
            fprintf(stderr, "cannot connect to second output port\n");
        }
    }
   
    jack_free(ports);
   
    printf("Sine wave generator running. Press Ctrl+C to stop.\n");
   
    // Keep running until interrupted
    while (sine_data.running) {
        sleep(1);
    }
   
    // Clean up
    jack_client_close(sine_data.client);
    printf("JACK client closed.\n");
   
    return 0;
}