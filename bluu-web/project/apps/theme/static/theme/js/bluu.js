/*jslint browser: true, devel: true*/
/*global jQuery, SET_ALERT_CONFIG_URL:false, SET_ALERT_URL:false */

var Bluu = (function ($) {
    "use strict";

    var set_alert = function (user_id, alert_id, device_id, duration, unit, text, email) {
            if (typeof SET_ALERT_URL !== 'undefined') {
                var data = {
                    'user': user_id,
                    'alert': alert_id,
                    'device_id': device_id,
                    'duration': duration,
                    'unit': unit,
                    'text_notification': text,
                    'email_notification': email
                };
                $.post(SET_ALERT_URL, data)
                    .done(function (data) {
                        alert("Data Loaded: " + data);
                    });
            } else {
                console.log('Error! SET_ALERT_URL is not defined.');
            }
        },
        set_alert_config = function (user_id, alert_id, duration, unit, text, email) {
            if (typeof SET_ALERT_CONFIG_URL !== 'undefined') {
                var data = {
                    'user': user_id,
                    'alert': alert_id,
                    'duration': duration,
                    'unit': unit,
                    'text_notification': text,
                    'email_notification': email
                };
                $.post(SET_ALERT_CONFIG_URL, data)
                    .done(function (data) {
                        alert("Data Loaded: " + data);
                    });
            } else {
                console.log('Error! SET_ALERT_URL is not defined.');
            }
        };

    return {
        set_alert: set_alert,
        set_alert_config: set_alert_config
    };

}(jQuery));
