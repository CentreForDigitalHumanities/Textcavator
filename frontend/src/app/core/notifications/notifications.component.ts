import { Component, OnDestroy } from '@angular/core';
import { Subscription } from 'rxjs';

import {
    Notification,
    NotificationService,
} from '@services/notification.service';

const notificationClassMap: {[T in Notification['type']]: NotificationDisplay['class']} = {
    info: 'is-info',
    warning: 'is-warning',
    danger: 'is-danger',
    success: 'is-success'
};

@Component({
    selector: 'ia-notifications',
    templateUrl: './notifications.component.html',
    styleUrls: ['./notifications.component.scss'],
    standalone: false
})
export class NotificationsComponent implements OnDestroy {
    defaultTimeout = 10000;

    subscription: Subscription;
    public notifications: NotificationDisplay[] = [];

    constructor(notificationService: NotificationService) {
        this.subscription = notificationService.observable.subscribe(
            (notification) => this.showNotification(notification)
        );
    }

    ngOnDestroy() {
        this.subscription.unsubscribe();
    }

    public remove(notification: NotificationDisplay) {
        notification.canDelete = false;
        notification.fadeOut = true;
        setTimeout(() => {
            this.notifications = this.notifications.filter(
                (candidate) => candidate !== notification
            );
            if (notification.timeout) {
                clearTimeout(notification.timeout);
            }
        }, 2000);
    }

    private showNotification(notification: Notification) {
        const notificationDisplay: NotificationDisplay = {
            canDelete: true,
            fadeOut: false,
            message: notification.message,
            class: notificationClassMap[notification.type],
            link: notification.link,
        };

        this.notifications.push(notificationDisplay);

        notificationDisplay.timeout = setTimeout(
            () => this.remove(notificationDisplay),
            this.defaultTimeout
        );
    }
}

interface NotificationDisplay {
    canDelete: boolean;
    fadeOut: boolean;
    message: string;
    // class type of the Bulma notification
    class: 'is-primary' | 'is-info' | 'is-success' | 'is-warning' | 'is-danger';
    timeout?;
    link?: {
        text: string;
        route: string[];
    };
}
