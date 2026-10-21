import { Component, OnDestroy } from '@angular/core';
import { Subscription } from 'rxjs';

import {
    Notification,
    NotificationService,
} from '@services/notification.service';

const notificationClassMap: {[T in Notification['type']]: string} = {
    info: 'bg-secondary text-bg-secondary',
    warning: 'bg-warning text-bg-warning',
    danger: 'bg-danger text-bg-danger',
    success: 'bg-success text-bg-success'
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
        this.notifications = this.notifications.filter(
            (candidate) => candidate !== notification
        );
    }

    private showNotification(notification: Notification) {
        const notificationDisplay: NotificationDisplay = {
            message: notification.message,
            class: notificationClassMap[notification.type],
            link: notification.link,
        };
        this.notifications.push(notificationDisplay);
    }
}

interface NotificationDisplay {
    message: string;
    class: string;
    link?: {
        text: string;
        route: string[];
    };
}
