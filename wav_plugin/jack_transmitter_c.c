#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <jack/jack.h>

typedef struct {
    jack_port_t *input_port;
    jack_port_t *output_port;
    jack_client_t *client;
} jack_data_t;

// Process callback - this is where audio processing happens
int process_callback(jack_nframes_t nframes, void *arg) {
    jack_data_t *data = (jack_data_t *)arg;
   
    // Get input and output buffers
    jack_default_audio_sample_t *in =
        (jack_default_audio_sample_t *)jack_port_get_buffer(data->input_port, nframes);
    jack_default_audio_sample_t *out =
        (jack_default_audio_sample_t *)jack_port_get_buffer(data->output_port, nframes);
   
    // Simple passthrough (copy input to output)
    memcpy(out, in, sizeof(jack_default_audio_sample_t) * nframes);
   
    return 0;
}

// Shutdown callback
void shutdown_callback(void *arg) {
    printf("JACK shutdown\n");
    exit(1);
}

int main(int argc, char *argv[]) {
    jack_data_t data;
    const char **ports;
    const char *client_name = "simple_client";
    jack_status_t status;
   
    // Open a client connection to the JACK server
    data.client = jack_client_open(client_name, JackNullOption, &status, NULL);
    if (data.client == NULL) {
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
        client_name = jack_get_client_name(data.client);
        fprintf(stderr, "unique name `%s' assigned\n", client_name);
    }
   
    // Set the process callback
    jack_set_process_callback(data.client, process_callback, &data);
   
    // Set shutdown callback
    jack_on_shutdown(data.client, shutdown_callback, &data);
   
    // Display sample rate
    printf("Sample rate: %d\n", jack_get_sample_rate(data.client));
   
    // Create input and output ports
    data.input_port = jack_port_register(data.client, "input",
                                        JACK_DEFAULT_AUDIO_TYPE,
                                        JackPortIsInput, 0);
    data.output_port = jack_port_register(data.client, "output",
                                         JACK_DEFAULT_AUDIO_TYPE,
                                         JackPortIsOutput, 0);
   
    if ((data.input_port == NULL) || (data.output_port == NULL)) {
        fprintf(stderr, "no more JACK ports available\n");
        return 1;
    }
   
    // Activate the client
    if (jack_activate(data.client)) {
        fprintf(stderr, "cannot activate client");
        return 1;
    }
   
    // Connect ports - find some physical ports to connect to
    ports = jack_get_ports(data.client, NULL, NULL,
                          JackPortIsPhysical | JackPortIsOutput);
    if (ports == NULL) {
        fprintf(stderr, "no physical capture ports\n");
        return 1;
    }
   
    // Connect first physical output to our input
    if (jack_connect(data.client, ports[0], jack_port_name(data.input_port))) {
        fprintf(stderr, "cannot connect input port\n");
    }

     // Connect first physical output to our input
    //if (jack_connect(data.client, ports[0], "audio_receiver:input")) {
     //   fprintf(stderr, "cannot connect input port\n");
    //}
   
    jack_free(ports);
   
    // Find physical input ports for our output
    ports = jack_get_ports(data.client, NULL, NULL,
                          JackPortIsPhysical | JackPortIsInput);
    if (ports == NULL) {
        fprintf(stderr, "no physical playback ports\n");
        return 1;
    }
   
    // Connect our output to first physical input
    if (jack_connect(data.client, jack_port_name(data.output_port), "audio_receiver:input")) {
        fprintf(stderr, "cannot connect output port\n");
    }
   
    jack_free(ports);
   
    printf("Client running. Press Enter to quit...\n");
    getchar();
   
    // Cleanup
    jack_client_close(data.client);
    return 0;
}