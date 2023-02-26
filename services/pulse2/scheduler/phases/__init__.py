# -*- coding: utf-8; -*-
# SPDX-FileCopyrightText: 2007-2008 Mandriva, http://www.mandriva.com/
# SPDX-FileCopyrightText: 2016-2023 Siveo <support@siveo.net> 
# SPDX-License-Identifier: GPL-2.0-or-later

def push_phases():
    from pulse2.scheduler.phases.remote import WOLPhase, UploadPhase, ExecutionPhase
    from pulse2.scheduler.phases.remote import DeletePhase, InventoryPhase
    from pulse2.scheduler.phases.remote import RebootPhase, HaltPhase, DonePhase
    from pulse2.scheduler.phases.remote import WUParsePhase
    from pulse2.scheduler.phases.imaging import PreImagingMenuPhase
    from pulse2.scheduler.phases.imaging import PostImagingMenuPhase

    return [PreImagingMenuPhase,
            WOLPhase,
            PostImagingMenuPhase,
            UploadPhase,
            ExecutionPhase,
            WUParsePhase,
            DeletePhase,
            InventoryPhase,
            RebootPhase,
            HaltPhase,
            DonePhase,
           ]
def pull_phases():
    from pulse2.scheduler.phases.pull import WOLPhase, UploadPhase, ExecutionPhase
    from pulse2.scheduler.phases.pull import DeletePhase, InventoryPhase
    from pulse2.scheduler.phases.pull import RebootPhase, HaltPhase
    from pulse2.scheduler.phases.remote import DonePhase
    from pulse2.scheduler.phases.remote import WUParsePhase

    return [WOLPhase,
            UploadPhase,
            ExecutionPhase,
            WUParsePhase,
            DeletePhase,
            InventoryPhase,
            RebootPhase,
            HaltPhase,
            DonePhase,
           ]

installed_phases = {"push": push_phases(),
                    "pull": pull_phases(),
                   }



__all__ = ["installed_phases"]
