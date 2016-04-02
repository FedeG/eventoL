from manager.api.rest.builder import count_by


def talks(talks):
    data = {
        'total': talks.count(),
        'talks_for_room': count_by(talks, lambda talk: talk.room.name),
        'talks_for_type': count_by(talks, lambda talk: talk.talk_proposal.type.name),
        'talks_for_level': count_by(talks, lambda talk: talk.talk_proposal.level)
    }
    return data


def proposals(proposals):
    data = {
        'talks_not_confirmed': proposals.filter(confirmed_talk=False).count(),
        'talks_confirmed': proposals.filter(confirmed_talk=True).count(),
        'total': proposals.count()
    }
    return data


def attendees(attendees):
    data = {
        'not_confirmed': attendees.filter(eventUser__assisted=False).count(),
        'confirmed': attendees.filter(eventUser__assisted=True).count(),
        'total': attendees.count()
    }
    return data


def installations(installations):
    data = {
        'total': installations.count(),
        'installation_for_software': count_by(installations, lambda inst: inst.software.name),
        'installation_for_hardware': count_by(installations, lambda inst: inst.hardware.type),
        'installation_for_installer': count_by(installations, lambda inst: inst.installer.collaborator.user.username)
    }
    return data


def installers(installers):
    data = {
        'total': installers.count(),
        'installers_for_level': count_by(installers, lambda inst: inst.level)
    }
    return data
